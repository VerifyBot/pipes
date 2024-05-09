import asyncio
from dataclasses import asdict
from sanic import Request, json

from .utils import checks
from ..database import Database
from ..models import User, Pipe
from ..decos import authorized

@authorized
async def route_get_runs(request: Request, db: Database, user: User):
  """Return the user's list of runs"""


  js = request.json
  err = await checks.validate_runs_info(js)

  if err:
    return json({"error": err})

  pipe: Pipe = await db.get_pipe(js["pipe_id"])

  if pipe is None:
    return json({"error": "invalid pipe"})

  if pipe.user_id != user.id:
    return json({"error": "you cannot access this pipe"})

  runs = await db.get_runs(**js)

  return json(dict(runs=[asdict(run) for run in runs]))

@authorized
async def route_get_run(request: Request, db: Database, user: User):
  """Return a run by ID"""

  run_id = request.json.get("id")

  if not run_id:
    return json({"error": "Missing run id"})

  run = await db.get_run(run_id)

  if run is None:
    return json({"error": "invalid run"})

  pipe = await db.get_pipe(run.pipe_id)

  if pipe.user_id != user.id:
    return json({"error": "you cannot access this run"})

  return json(dict(run=asdict(run)))