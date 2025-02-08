import os
import redis
from redis.exceptions import ConnectionError
from typing import Generator
from dotenv import load_dotenv


load_dotenv()

host_redis = os.getenv("REDIS_HOST", default="localhost")
port_redis = os.getenv("REDIS_PORT", default=6379)


class RedisSupport:

    def __init__(self):
        try:
            redis_pool = redis.ConnectionPool(
                                                host=host_redis,
                                                port=port_redis,
                                                decode_responses=True)
            self._redis = redis.Redis(connection_pool=redis_pool)
            self._redis.ping()
        except ConnectionError:
            raise ConnectionError("Redis is not ready.")


    def init(self):
        return self._redis


instance = RedisSupport()

def get_redis() -> Generator:
    session = instance.init()
    yield session
