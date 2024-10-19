from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import URL
from sqlalchemy.ext.declarative import declarative_base


url = URL.create(
    drivername = 'postgresql',
    username = 'postgres',
    password = 'admin',
    host = 'localhost',
    port = 5432,
    database = 'fastapi_blog_db')


engine = create_engine(url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()