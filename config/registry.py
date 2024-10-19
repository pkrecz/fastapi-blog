import logging
from config.database import engine

# app_blog imports ...
from app_blog import models as blog_models
from app_blog import controlers as blog_controlers


logger = logging.getLogger('uvicorn.error')


def create_tables():
    blog_models.Base.metadata.create_all(bind=engine)
    logger.info('Tables has been created.')


def load_routers(application):

    application.include_router(router=blog_controlers.router_user,
                                prefix='/admin',
                                tags=['Authentication'])

    application.include_router(router=blog_controlers.router_blog,
                                prefix='/blog',
                                tags=['Blog'])
    logger.info('Routes has been loaded.')
