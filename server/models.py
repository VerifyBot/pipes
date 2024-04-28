from dataclasses import dataclass
from datetime import datetime

import enum


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
