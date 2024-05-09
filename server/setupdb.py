# setup db based on the models

import asyncio
import logging
import configparser

import asyncpg
import coloredlogs

coloredlogs.install(level="INFO")

tabels = dict(
  users="""
  CREATE TABLE users (
    id TEXT PRIMARY KEY,
    email TEXT,
    username TEXT,
    avatar TEXT,
    
    role TEXT DEFAULT 'user',
    access_token TEXT,
    refresh_token TEXT,
    expires_at TIMESTAMP,
    token TEXT
  );
  """,

  pipes="""
  CREATE TABLE pipes (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE, 
    description TEXT NOT NULL,
    webhook_url TEXT NOT NULL,
    hmac_header TEXT DEFAULT NULL,
    hmac_secret TEXT DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    last_run TIMESTAMP,
    total_runs INTEGER DEFAULT 0
  );
  """,

  # keep track of the executed runs
  runs="""
  CREATE TABLE runs (
    id TEXT PRIMARY KEY,
    pipe_id TEXT NOT NULL REFERENCES pipes(id) ON DELETE CASCADE,
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    success BOOLEAN,
    error TEXT,
    
    -- the request of the webhook initializer
    request_info JSONB,
    
    -- the response from discord
    response_info JSONB
  );
  """
)


async def setup_db(pool: asyncpg.Pool, redo: list = None):
  async with pool.acquire() as conn:
    for table in tabels:
      if redo:
        if table not in redo:
          continue

        logging.info(f"Dropping table {table}")
        await conn.execute(f"DROP TABLE IF EXISTS {table} CASCADE;")

        if table == 'runs':
          logging.info("^ Resetting total_runs from pipes")
          await conn.execute("UPDATE pipes SET total_runs = 0")

      logging.info(f"Creating table {table}")
      await conn.execute(tabels[table])


async def main(*args, **kwargs):
  config = configparser.ConfigParser()
  config.read("config.ini")

  logging.info("Connecting to the database")
  async with asyncpg.create_pool(
      user=config.get("database", "username"),
      password=config.get("database", "password"),
      database=config.get("database", "database"),
  ) as pool:
    logging.info("Setting up the database")
    await setup_db(pool, *args, **kwargs)


if __name__ == "__main__":
  loop = asyncio.get_event_loop()
  loop.run_until_complete(main(redo=["runs"]))
