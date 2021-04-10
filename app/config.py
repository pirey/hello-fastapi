import os
from functools import lru_cache

from pydantic import BaseSettings


class Settings(BaseSettings):
    database_url: str

env = os.getenv("ENV") or ""
env_file = f"{env}.env"
_settings = Settings(_env_file=env_file)

def get_settings():
    return _settings
