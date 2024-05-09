import json
import typing
import uuid
from typing import List

import asyncpg

from .models import User, Pipe, RunInfo, Run


class Database:
  def __init__(self, pool: asyncpg.Pool):
    self.pool = pool

  ## PIPES QUERIES ##

  async def get_pipes(self, user: User) -> list[Pipe]:
    """Return the user's list of pipes"""

    raw_pipes = await self.pool.fetch("SELECT * FROM pipes WHERE user_id = $1", user.id)
    return [Pipe(**pipe) for pipe in raw_pipes]

  async def get_pipe(self, pipe_id: str) -> Pipe:
    """Return a pipe by ID"""

    raw_pipe = await self.pool.fetchrow("SELECT * FROM pipes WHERE id = $1", pipe_id)
    return Pipe(**raw_pipe) if raw_pipe else None

  async def add_pipe(self, user: User, description: str, webhook_url: str, hmac_header: str = None, hmac_secret: str = None, **kw) -> Pipe:
    """Add a pipe to the user's list of pipes and return the pipe object."""

    pipe_id = uuid.uuid4().hex[:8]

    raw_pipe = await self.pool.fetchrow(
      """
      INSERT INTO pipes (id, user_id, description, webhook_url, hmac_header, hmac_secret)
      VALUES ($1, $2, $3, $4, $5, $6)
      RETURNING *
      """,
      pipe_id, user.id, description, webhook_url, hmac_header, hmac_secret
    )
    return Pipe(**raw_pipe)

  async def edit_pipe(self, pipe_id: str, user: User, description: str, webhook_url: str,
                      hmac_header: str = None, hmac_secret: str = None, **kw) -> Pipe:
    """Edit a pipe by ID, checking if the user owns the pipe. Return the pipe object."""

    raw_pipe = await self.pool.fetchrow(
      """
      UPDATE pipes
      SET description = $1, webhook_url = $2, updated_at = NOW(), hmac_header = $3, hmac_secret = $4
      WHERE id = $5 AND user_id = $6
      RETURNING *
      """,
      description, webhook_url, hmac_header, hmac_secret,
      pipe_id, user.id
    )
    return Pipe(**raw_pipe)

  async def delete_pipe(self, pipe_id: str, user: User = None):
    """Delete a pipe by ID, optionally checking if the user owns the pipe."""

    if user is None:
      await self.pool.execute("DELETE FROM pipes WHERE id = $1", pipe_id)
    else:
      await self.pool.execute("DELETE FROM pipes WHERE id = $1 AND user_id = $2", pipe_id, user.id)

  async def pipe_run(self, pipe: Pipe):
    """Update the pipe's runs count and last run."""

    await self.pool.execute(
      """
      UPDATE pipes
      SET total_runs = total_runs + 1, last_run = NOW()
      WHERE id = $1
      """,
      pipe.id
    )

  ## USER QUERIES ##

  async def get_user(self, value: str, by: str = "token") -> typing.Optional[User]:
    """Return the user object from the database given the "by"."""
    assert by in ("id", "token"), "Invalid 'by' value"

    raw_user = await self.pool.fetchrow(f"SELECT * FROM users WHERE {by} = $1", value)
    return User(**raw_user) if raw_user else None

  async def add_user(self, user: User) -> None:
    """Add a user to the database."""
    await self.pool.execute(
      """
      INSERT INTO users (id, email, username, avatar, role, access_token, refresh_token, expires_at, token)
      VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
      """,
      user.id, user.email, user.username, user.avatar, user.role, user.access_token, user.refresh_token,
      user.expires_at, user.token
    )

  ## RUNS QUERIES ##

  async def log_run(self, pipe_id: str, success: bool, error: str = None, request_info: dict = None, response_info: dict = None):
    """Log a run for a pipe."""

    run_id = uuid.uuid4().hex[:8]

    await self.pool.execute(
      """
      INSERT INTO runs (id, pipe_id, success, error, request_info, response_info)
      VALUES ($1, $2, $3, $4, $5, $6)
      """,
      run_id, pipe_id, success, error, json.dumps(request_info), json.dumps(response_info)
    )


  async def get_runs(self, pipe_id: str, offset: int, limit: int) -> list[RunInfo]:
    """Return the runs for the pipe id"""


    raw_runs = await self.pool.fetch(
      """
      SELECT id, pipe_id, sent_at, success FROM runs WHERE pipe_id = $1 ORDER BY sent_at DESC OFFSET $2 LIMIT $3
      """,
      pipe_id, offset, limit
    )

    return [RunInfo(**run) for run in raw_runs]


  async def get_run(self, run_id: str) -> RunInfo:
    """Return a run by ID"""

    raw_run = await self.pool.fetchrow("SELECT * FROM runs WHERE id = $1", run_id)
    return Run(**raw_run) if raw_run else None