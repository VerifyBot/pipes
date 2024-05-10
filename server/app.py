from sanic import Sanic, Blueprint
from sanic_ext import Extend

import asyncpg
from aiocache import SimpleMemoryCache

import configparser
import logging

from .database import Database


class Pipes:
  def __init__(self, *args, app: Sanic, config: configparser.ConfigParser, mode: str = "dev", **kwargs):
    self.app = app
    self.config = config

    # CORS for all origins. todo: change this to the website url
    app.config.CORS_ORIGINS = "*"
    Extend(app)

    # register listeners for database connection
    self.register_listeners()

    ## Global Variables ##
    self.setup_globals(mode)

    ## Routes ##
    self.load_routes()

  def register_listeners(self):
    self.app.register_listener(self.setup_hook, "before_server_start")
    self.app.register_listener(self.close_hook, "before_server_stop")

  def setup_globals(self, mode: str):
    # debug if is windows. todo: change this to a different create_app method, so sanic server:dev or server:prod can be used
    DEBUG_MODE = mode == "dev"
    server_section = "app" if DEBUG_MODE else "prod_app"

    self.app.ctx.states_cache = SimpleMemoryCache(ttl=300)

    self.app.ctx.config = self.config
    self.app.ctx.DEBUG_MODE = DEBUG_MODE
    self.app.ctx.APP_ADMINS = set(int(uid) for uid in self.config.get("misc", "admins").split(","))
    self.app.ctx.SERVER_URL = self.config.get(server_section, "server_url")
    self.app.ctx.WEBSITE_URL = self.config.get(server_section, "website_url")

    pipe_path = self.config.get(server_section, "pipe_path")
    self.app.ctx.WILDCARD_PIPE_REGEX = pipe_path.split(':')[0].replace('$', r'^([^.]+)').replace('.', r'\.') + '$'

  def load_routes(self):
    # OAuth
    from .routes.oauth2 import route_connect, route_callback

    oauth2 = Blueprint("oauth2", url_prefix="/oauth2")
    oauth2.add_route(route_connect, "/connect")
    oauth2.add_route(route_callback, "/callback")
    self.app.blueprint(oauth2)

    # App
    from .routes.pipe import route_get_pipes, route_add_pipe, route_edit_pipe, route_delete_pipe, route_get_pipe

    self.app.add_route(route_get_pipes, "/pipes")
    self.app.add_route(route_get_pipe, "/pipe", methods=["POST"])
    self.app.add_route(route_add_pipe, "/add_pipe", methods=["POST"])
    self.app.add_route(route_edit_pipe, "/edit_pipe", methods=["POST"])
    self.app.add_route(route_delete_pipe, "/delete_pipe", methods=["POST"])

    from .routes.webhook import route_webhook_handler

    self.app.add_route(route_webhook_handler, "/", methods=["POST"])

    from .routes.runs import route_get_runs, route_get_run

    self.app.add_route(route_get_runs, "/runs", methods=["POST"])
    self.app.add_route(route_get_run, "/run", methods=["POST"])

    from .routes.misc import route_hello, route_health

    self.app.add_route(route_hello, "/", methods=["GET"])
    self.app.add_route(route_health, "/health", methods=["GET"])

  async def setup_hook(self, app: Sanic):
    logging.info("Setting up db connection")

    pool = await asyncpg.create_pool(
      user=self.config.get("database", "username"),
      password=self.config.get("database", "password"),
      database=self.config.get("database", "database"),
    )

    db_conn = Database(pool)
    app.ctx.db = db_conn
    app.ext.dependency(db_conn, name="db")

  async def close_hook(self, app: Sanic):
    logging.info("Closing db connection")
    db_conn: Database = app.ctx.db
    await db_conn.pool.close()
