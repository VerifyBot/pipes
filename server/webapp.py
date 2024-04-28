import os
from dataclasses import asdict
import configparser
import logging
import uuid
from urllib.parse import urlencode
from datetime import datetime, timedelta

import coloredlogs
from sanic import Sanic, Request, json, redirect
import asyncpg
from aiocache import SimpleMemoryCache

from .models import User, RoleEnum
from .database import Database
from .decos import authorized

app = Sanic("Pipes")

DEBUG_MODE = True

# since we're running this as a module, the current working directory is the parent directory
# so we need to change it to the server directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

print("Current working directory:", os.getcwd())

config = configparser.ConfigParser()
config.read("./config.ini")

APP_ADMINS = set(int(uid) for uid in config.get("app", "admins").split(","))
WEBSITE_URL = config.get("server" if DEBUG_MODE else "prod_server", "url")

coloredlogs.install(level="INFO")


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
app.ctx.WEBSITE_URL = WEBSITE_URL
app.ctx.config = config

# OAuth
from sanic import Blueprint

# OAuth
from .routes.oauth2 import route_connect, route_callback

oauth2 = Blueprint("oauth2", url_prefix="/oauth2")
oauth2.add_route(route_connect, "/connect")
oauth2.add_route(route_callback, "/callback")
app.blueprint(oauth2)

# App
from .routes.app import route_pipes

app.add_route(route_pipes, "/pipes")
