from dataclasses import asdict
from sanic import Request, json
from ..database import Database
from ..models import User
from ..decos import authorized

# App
# GET /pipes
@authorized
async def route_pipes(request: Request, db: Database, user: User):
  """Return the user's list of pipes"""

  pipes = await db.get_pipes(user)

  return json(dict(pipes=[asdict(pipe) for pipe in pipes]))
