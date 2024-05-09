import logging

from sanic import Request, json
from ..database import Database
from ..models import Pipe

import json as json_lib
import aiohttp
import hmac
import hashlib
import io
import re
import typing


async def send_webhook(pipe: Pipe, body: str):
  """
  Send the webhook to the pipe webhook_url

  This function handles:
  - The case where the body is too big to be sent as content (a file is sent instead)
  - TODO: Discord Ratelimits and retries
  """

  if len(body) <= 2000:
    post_kwargs = dict(json=dict(content=body))
  else:
    # send as a file
    buffer = io.BytesIO(body.encode())
    buffer.seek(0)
    form_data = aiohttp.FormData(quote_fields=False)
    form_data.add_field(name='files[0]', value=buffer, filename='content.txt', content_type='application/octet-stream')
    post_kwargs = dict(data=form_data)

  async with aiohttp.ClientSession() as cs:
    async with cs.post(pipe.webhook_url, **post_kwargs) as resp:
      if not resp.ok:
        return resp, await resp.text(), True
      return resp, None, False


async def handle_webhook_request(request: Request, db: Database, pipe_id: str) -> dict:
  """
  Handle the webhook request from a domain <pipeid>.m.pipes.me
  and send the webhook to Discord if the pipe/request is valid.
  """

  pipe = await db.get_pipe(pipe_id)

  if pipe is None:
    return {"error": "invalid pipe"}

  if not pipe.is_active:
    return {"error": "pipe is not active"}

  body = request.body.decode('utf-8')

  if not body:
    return {"error": "empty body"}

  if pipe.hmac_header and pipe.hmac_secret:  # verify hmac
    given_signature = request.headers.get(pipe.hmac_header)

    if not given_signature:
      return {"error": "hmac signature missing"}

    # print(f'verifying hmac with {pipe.hmac_secret=} and body: {request.body[:10]}...')
    expected_signature = hmac.new(pipe.hmac_secret.encode(), request.body, hashlib.sha256).hexdigest()
    # print('expected_signature', expected_signature)
    # print('given_signature', given_signature)

    # fixit: i think that this is not secure, but i have to comply with intergations like
    # github that send the signature as sha256=... ¯\_(ツ)_/¯
    if given_signature and expected_signature not in given_signature:
      return {"error": "invalid hmac signature"}

  resp, txt, has_err = await send_webhook(pipe, body)

  if has_err:
    return {'error': txt, 'resp': resp}

  return {'status': 'ok', 'resp': resp}


async def route_webhook_handler(request: Request, db: Database):
  # print(request.server_name)
  # print(WILDCARD_PIPE_REGEX)

  mt = re.match(request.app.ctx.WILDCARD_PIPE_REGEX, request.server_name)

  if mt is None:
    return json({"error": "invalid pipe"})

  pipe_id = mt.group(1)

  # does the pipe exist?
  pipe = await db.get_pipe(pipe_id)

  if pipe is None:
    return json({"error": "invalid pipe"})

  try:
    resp = await handle_webhook_request(request, db, pipe_id)
  except Exception as e:
    logging.error(f"Error handling webhook request", exc_info=e)
    resp = {'error': 'internal error'}  # todo.. the developers have been notified... notify!

  finally:
    # update runs
    await db.pipe_run(pipe)

  req_resp: typing.Optional[aiohttp.ClientResponse] = resp.pop('resp', None)

  success = 'error' not in resp
  error = resp.get('error')

  request_info = {
    "headers": dict(request.headers),
    "ip": request.client_ip,
    "body": request.body.decode('utf-8')
  }

  response_info = None
  if req_resp:
    response_info = {
      "status": req_resp.status,
      "headers": dict(req_resp.headers),
      "body": await req_resp.text() if req_resp.status != 204 else None
    }

  await db.log_run(pipe_id, success, error, request_info=request_info, response_info=response_info)

  return json(resp)
