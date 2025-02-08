import os
from functools import lru_cache
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):

    title: str = "Blog"
    version: str = "1.0.0"
    docs_url: str = "/swagger"

    ACCESS_SECRET_KEY: str = str(os.getenv("ACCESS_SECRET_KEY"))
    REFRESH_SECRET_KEY: str = str(os.getenv("REFRESH_SECRET_KEY"))
    ALGORITHM: str = str(os.getenv("ALGORITHM"))
    DATABASE_URL_LOCAL: str = str(os.getenv("DATABASE_URL_LOCAL"))
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 120
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7
    MEDIA_ROOT: str = str(os.getenv("MEDIA_ROOT"))
    MEDIA_URL: str = str(os.getenv("MEDIA_URL"))
    MAX_FILE_SIZE: int = 1024 * 1024


@lru_cache(maxsize=None, typed=False)
def get_settings():
    return Settings()

settings = get_settings()
