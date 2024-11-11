from typing import Optional
from fastapi_filter import FilterDepends
from fastapi_filter.contrib.sqlalchemy import Filter
from .models import UserModel, PostModel


class UserFilter(Filter):
    username: Optional[str] = None

    class Constants(Filter.Constants):
        model = UserModel


class PostOwnFilter(Filter):

    title__like: Optional[str] = None
    published: Optional[bool] = None
    search: Optional[str] = None
    order_by: Optional[list[str]] = None

    class Constants(Filter.Constants):
        model = PostModel
        search_model_fields = ["content"]


class PostFindFilter(Filter):

    title__like: Optional[str] = None
    published: Optional[bool] = None
    order_by: Optional[list[str]] = None
    users: Optional[UserFilter] = FilterDepends(UserFilter)

    class Constants(Filter.Constants):
        model = PostModel
