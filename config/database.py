import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy.exc import DatabaseError, SQLAlchemyError
from dotenv import load_dotenv
from .settings import settings
from .util import Singleton
from .redis import get_redis


redis_session = get_redis()

class Base(DeclarativeBase):
    pass


load_dotenv()
url = os.getenv("DATABASE_URL", default=settings.DATABASE_URL_LOCAL)


def get_engine(db_url: str = url):
    cached_value = redis_session.get("db_url")
    if cached_value is not None:
        url = cached_value
    else:
        redis_session.set("db_url", db_url, ex=3600)
        url = db_url
    return create_engine(url=url, pool_pre_ping=True)


def get_session():
    session = sessionmaker(autocommit=False, autoflush=False, bind=get_engine())
    return session()


class DatabaseSessionClass(metaclass=Singleton):

    def __enter__(self):
        self.db = get_session()
        return self.db

    def __exit__(self, exc_type, exc_value: str, exc_traceback: str) -> None:
        try:
            if any([exc_type, exc_value, exc_traceback]):
                raise
            self.db.commit()
        except (SQLAlchemyError, DatabaseError, Exception) as exception:
            self.db.rollback()
            raise exception
        finally:
            self.db.close()


def get_db():
    with DatabaseSessionClass() as db:
        yield db
