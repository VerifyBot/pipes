import asyncio
from dataclasses import asdict
from sanic import Request, json
from ..database import Database
from ..models import User
from ..decos import authorized

from .utils import checks


# App
# GET /pipes
@authorized
async def route_get_pipes(request: Request, db: Database, user: User):
  """Return the user's list of pipes"""
  pipes = await db.get_pipes(user)
  return json(dict(pipes=[asdict(pipe) for pipe in pipes]))

@authorized
async def route_get_pipe(request: Request, db: Database, user: User):
  """Return a pipe by ID, and its recent runs."""
  pipe_id = request.json.get("id")

  if not pipe_id:
    return json({"error": "Missing pipe id"})

  pipe = await db.get_pipe(pipe_id)

  if pipe is None or pipe.user_id != user.id:
    return json({"error": "invalid pipe"})

  return json(dict(
    pipe=asdict(pipe),
    runs=[asdict(run) for run in await db.get_runs(pipe_id, 0, 15)]
  ))

@authorized
async def route_add_pipe(request: Request, db: Database, user: User):
  """Add a pipe to the user's list of pipes"""

  js = request.json
  err = await checks.validate_pipe_info(js)

  if err:
    return json({"error": err})

  pipe = await db.add_pipe(user, **js)

  return json(asdict(pipe))


@authorized
async def route_delete_pipe(request: Request, db: Database, user: User):
  """Delete a pipe from the user's list of pipes"""

  pipe_id = request.json.get("id")

  if not pipe_id:
    return json({"error": "Missing pipe id"})

  await db.delete_pipe(pipe_id, user)

  return json({"status": "ok"})


@authorized
async def route_edit_pipe(request: Request, db: Database, user: User):
  """Edit a pipe from the user's list of pipes"""

  pipe_id = request.json.get("id")

  if not pipe_id:
    return json({"error": "Missing pipe id"})

  js = request.json
  err = await checks.validate_pipe_info(js)

  if err:
    return json({"error": err})

  pipe = await db.edit_pipe(pipe_id, user, **js)

  return json(asdict(pipe))
