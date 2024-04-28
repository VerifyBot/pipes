import typing

import asyncpg

from .models import User, Pipe


class Database:
  def __init__(self, pool: asyncpg.Pool):
    self.pool = pool

  async def get_pipes(self, user: User) -> list[Pipe]:
    """Return the user's list of pipes"""

    raw_pipes = await self.pool.fetch("SELECT * FROM pipes WHERE user_id = $1", user.id)
    return [Pipe(**pipe) for pipe in raw_pipes]

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
