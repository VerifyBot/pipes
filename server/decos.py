from functools import wraps

from sanic.response import json
from sanic import Request

from .database import Database


def authorized(func):
  """
  Check if the user is authorized to access the endpoint
  This is done by checking is the provided token in the Authorization header
  is in the database.

  If the user is authorized, the user object is added to the request context
  """

  @wraps(func)
  async def wrapper(request: Request, *args, **kwargs):
    # get the database dependency
    db: Database = request.app.ctx._dependencies.db

    # get the token from the Authorization header
    token = request.headers.get("Authorization")

    if not token:
      return json({"error": "unauthorized", "msg": "Authorization header is required"})

    # check if the token is in the database
    user = await db.get_user(token)

    if not user:
      return json({"error": "unauthorized", "msg": "Invalid token"})

    # inject the user object as a parameter
    kwargs["user"] = user

    return await func(request, *args, **kwargs)

  return wrapper
