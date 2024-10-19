from fastapi import FastAPI
from config.settings import settings
from config import registry


def start_application():
    app = FastAPI(
                    title=settings.title,
                    version=settings.version)
    registry.create_tables()
    registry.load_routers(app)
    return app


app = start_application()
