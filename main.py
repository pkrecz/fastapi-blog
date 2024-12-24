from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from config.settings import settings
from config import registry


def lifespan(app: FastAPI):
    registry.init_models()
    registry.init_routers(app)
    app.mount(settings.MEDIA_URL, StaticFiles(directory=settings.MEDIA_ROOT))
    yield


app = FastAPI(
                lifespan=lifespan,
                title=settings.title,
                version=settings.version,
                docs_url=settings.docs_url,
                redoc_url=None,
                contact={
                            "name": "Piotr",
                            "email": "pkrecz@poczta.onet.pl"})
