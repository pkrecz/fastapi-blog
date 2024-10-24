import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
from .settings import settings


load_dotenv()


url_docker = os.getenv('DATABASE_URL')
if url_docker is not None:
    url = url_docker
else:
    url = settings.DATABASE_URL_LOCAL


engine = create_engine(url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
