import logging
from config.database import Base, get_engine
from app_blog import controlers as blog_controlers


logger = logging.getLogger("uvicorn.error")


def init_models():
    Base.metadata.create_all(bind=get_engine())
    logger.info("Tables has been created.")


def init_routers(application):
    application.include_router(
                                router=blog_controlers.router_auth,
                                prefix="/admin",
                                tags=["Authentication"])
    application.include_router(
                                router=blog_controlers.router_blog,
                                prefix="/blog",
                                tags=["Blog"])
    logger.info("Routes has been loaded.")
