import os
from functools import lru_cache

from pydantic import BaseSettings


class Settings(BaseSettings):
    database_url: str


@lru_cache
def get_settings():
    env = os.getenv("ENV") or ""
    env_file = f"{env}.env"
    return Settings(_env_file=env_file)
