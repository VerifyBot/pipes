from dataclasses import dataclass
from datetime import datetime

import enum

import humanize


class RoleEnum(str, enum.Enum):  # use enum.StrEnum in Python 3.11+
  admin = 'admin'
  user = 'user'

  def __str__(self):
    return self.value


@dataclass
class User:
  id: str
  email: str
  username: str
  avatar: str

  role: RoleEnum

  access_token: str
  refresh_token: str
  expires_at: datetime
  token: str


@dataclass
class Pipe:
  id: str

  user_id: str

  description: str
  webhook_url: str

  created_at: datetime
  updated_at: datetime

  is_active: bool

  last_run: datetime
  total_runs: int

  hmac_header: str = None
  hmac_secret: str = None
  url: str = None
  last_run_human: str = None
  last_run_ts: int = None

  def __post_init__(self):
    from .webapp import config, server_section  # apparently it isn't a circular import if we import here
    self.url = config.get(server_section, 'pipe_path').replace('$', self.id)

    if self.last_run:
      self.last_run_ts = int(self.last_run.timestamp())
      self.last_run_human = humanize.naturaltime(datetime.now() - self.last_run)
