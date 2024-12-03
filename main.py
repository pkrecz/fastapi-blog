from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from config.settings import settings
from config import registry


def start_application():

    app = FastAPI(
                    title=settings.title,
                    version=settings.version,
                    docs_url=settings.docs_url,
                    redoc_url=None,
                    contact={
                                "name": "Piotr",
                                "email": "pkrecz@poczta.onet.pl"})

    app.mount(settings.MEDIA_URL, StaticFiles(directory=settings.MEDIA_ROOT))

    registry.create_tables()
    registry.load_routers(app)
    return app


app = start_application()
