import hashlib
import hmac
import io

import aiohttp
from sanic import Sanic, Blueprint, Request, json, text, HTTPResponse
from sanic_ext import Extend

import asyncpg
from aiocache import SimpleMemoryCache

import re
import os
import configparser
import coloredlogs
import logging

from .database import Database

import json as json_lib

coloredlogs.install(level="INFO")

app = Sanic("Pipes", dumps=lambda obj: json_lib.dumps(obj, default=str))
app.config.CORS_ORIGINS = "*"
Extend(app)

# debug if is windows
DEBUG_MODE = os.name == 'nt'

# since we're running this as a module, the current working directory is the parent directory
# so we need to change it to the server directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

logging.info(f"Current working directory: {os.getcwd()}", )

config = configparser.ConfigParser()
config.read("./config.ini")

APP_ADMINS = set(int(uid) for uid in config.get("misc", "admins").split(","))

server_section = "app" if DEBUG_MODE else "prod_app"
SERVER_URL = config.get(server_section, "server_url")
WEBSITE_URL = config.get(server_section, "website_url")
WILDCARD_PIPE_REGEX = config.get(server_section, "wildcard_pipe_regex")


@app.before_server_start
async def setup_db(app: Sanic, _):
  pool = await asyncpg.create_pool(
    user=config.get("database", "username"),
    password=config.get("database", "password"),
    database=config.get("database", "database"),
  )

  db_conn = Database(pool)
  app.ctx.db = db_conn
  app.ext.dependency(db_conn, name="db")


@app.before_server_stop
async def close_db(app: Sanic):
  print("Closing db connection")
  db_conn: Database = app.ctx.db
  await db_conn.pool.close()


## Global Variables ##
app.ctx.states_cache = SimpleMemoryCache(ttl=300)
app.ctx.SERVER_URL = SERVER_URL
app.ctx.WEBSITE_URL = WEBSITE_URL
app.ctx.APP_ADMINS = APP_ADMINS
app.ctx.config = config


@app.get('/')
async def index_get(request: Request):
  return text("Hello, World!")


@app.get('/health')
async def health(request: Request):
  # just return status code ok. no body
  return HTTPResponse(status=204, content_type='text/plain; charset=utf-8')


@app.post('/')
async def webhook_handler(request: Request, db: Database):
  # needs to be in a format <any>.0.tcp.eu.ngrok.io, i want the <any>

  mt = re.match(WILDCARD_PIPE_REGEX, request.server_name)

  if mt is None:
    return json({"error": "invalid pipe"})

  pipe_id = mt.group(1)

  pipe = await db.get_pipe(pipe_id)

  if pipe is None:
    return json({"error": "invalid pipe"})

  if not pipe.is_active:
    return json({"error": "pipe is not active"})

  body = request.body.decode('utf-8')


  if pipe.hmac_header and pipe.hmac_secret:  # verify hmac
    given_signature = request.headers.get(pipe.hmac_header)

    if not given_signature:
      return json({"error": "hmac signature missing"})

    # print(f'verifying hmac with {pipe.hmac_secret=} and body: {request.body[:10]}...')
    expected_signature = hmac.new(pipe.hmac_secret.encode(), request.body, hashlib.sha256).hexdigest()
    # print('expected_signature', expected_signature)
    # print('given_signature', given_signature)

    # fixit: i think that this is not secure, but i have to comply with intergations like
    # github that send the signature as sha256=... ¯\_(ツ)_/¯
    if given_signature and expected_signature not in given_signature:
      return json({"error": "invalid hmac signature"})

  msg = {'status': 'ok'}

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
        msg = {'error': f'webhook failed: {await resp.text()}'}

  # update runs
  await db.pipe_run(pipe)

  return json(msg)


# OAuth
from .routes.oauth2 import route_connect, route_callback

oauth2 = Blueprint("oauth2", url_prefix="/oauth2")
oauth2.add_route(route_connect, "/connect")
oauth2.add_route(route_callback, "/callback")
app.blueprint(oauth2)

# App
from .routes.pipe import route_get_pipes, route_add_pipe, route_edit_pipe, route_delete_pipe

app.add_route(route_get_pipes, "/pipes")
app.add_route(route_add_pipe, "/add_pipe", methods=["POST"])
app.add_route(route_edit_pipe, "/edit_pipe", methods=["POST"])
app.add_route(route_delete_pipe, "/delete_pipe", methods=["POST"])
