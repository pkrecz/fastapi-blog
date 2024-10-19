from pydantic_settings import BaseSettings


class Settings(BaseSettings):

    title: str = 'Blog'
    version: str = '1.0.0'

    ACCESS_SECRET_KEY: str = '39857747a1a0a2abcc4b467d2a9732e9f004c25028c07de242088143fc37085a2e23f22aff8859c9fb31c6b98e188fe314390f14f7030565642abc9df44aab1bd'
    REFRESH_SECRET_KEY: str = '0d0590e8eb2b6098207111b2b7e4f748472d07e99daa2d813fb703dafe60de7b833050e6b3d7bb9e3fab098d5e63ddbc03cebdcafd0942431e6fab9692e94aa6'
    ALGORITHM: str = 'HS256'
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7


settings = Settings()
