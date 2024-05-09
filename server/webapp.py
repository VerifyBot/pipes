from sanic import Sanic, Blueprint, Request, json, text, HTTPResponse
from sanic_ext import Extend

import asyncpg
from aiocache import SimpleMemoryCache

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
WILDCARD_PIPE_REGEX = config.get(server_section, "pipe_path").split(':')[0] \
                        .replace('$', r'^([^.]+)').replace('.', r'\.') + '$'


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
app.ctx.WILDCARD_PIPE_REGEX = WILDCARD_PIPE_REGEX
app.ctx.config = config


@app.get('/')
async def index_get(request: Request):
  return text("Hello, World!")

@app.get('/health')
async def health(request: Request):
  # just return status code ok. no body
  return HTTPResponse(status=204, content_type='text/plain; charset=utf-8')




## Routes ##

# OAuth
from .routes.oauth2 import route_connect, route_callback

oauth2 = Blueprint("oauth2", url_prefix="/oauth2")
oauth2.add_route(route_connect, "/connect")
oauth2.add_route(route_callback, "/callback")
app.blueprint(oauth2)

# App
from .routes.pipe import route_get_pipes, route_add_pipe, route_edit_pipe, route_delete_pipe, route_get_pipe

app.add_route(route_get_pipes, "/pipes")
app.add_route(route_get_pipe, "/pipe", methods=["POST"])
app.add_route(route_add_pipe, "/add_pipe", methods=["POST"])
app.add_route(route_edit_pipe, "/edit_pipe", methods=["POST"])
app.add_route(route_delete_pipe, "/delete_pipe", methods=["POST"])

from .routes.webhook import route_webhook_handler

app.add_route(route_webhook_handler, "/", methods=["POST"])

from .routes.runs import route_get_runs, route_get_run

app.add_route(route_get_runs, "/runs", methods=["POST"])
app.add_route(route_get_run, "/run", methods=["POST"])