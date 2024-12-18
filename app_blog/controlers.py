from fastapi import APIRouter, status, Depends, Form, Request
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_filter import FilterDepends
from sqlalchemy.orm import Session
from fastapi_restful.cbv import cbv
from config.database import get_db
from .schemas import (UserCreateBase, UserViewBase, UserUpdateBase, UserChangePasswordBase,
                      TokenAccessRefreshBase, TokenAccessBase,
                      PostCreateBase, PostUpdateBase, PostViewBase)
from .models import UserModel
from .filters import PostOwnFilter, PostFindFilter
from .service import AuthenticationService, BlogService
from .dependency import Dependency


router_auth = APIRouter()
router_blog = APIRouter()
dependency = Dependency()


@cbv(router_auth)
class APIAuthClass:

    db: Session = Depends(get_db)


    @router_auth.post(path="/register/", status_code=status.HTTP_201_CREATED, response_model=UserViewBase)
    async def register_user(
                            self,
                            data: UserCreateBase):
        service = AuthenticationService(db=self.db)
        return service.auth_register_user(data=data)


    @router_auth.put(path="/update/", status_code=status.HTTP_200_OK, response_model=UserViewBase)
    async def update_user(
                            self,
                            data: UserUpdateBase,
                            cuser: UserModel = Depends(dependency.log_dependency)):
        service = AuthenticationService(db=self.db, cuser=cuser)
        return service.auth_update_user(data=data)


    @router_auth.delete(path="/delete/", status_code=status.HTTP_200_OK)
    async def delete_user(
                            self,
                            cuser: UserModel = Depends(dependency.log_dependency)):
        service = AuthenticationService(db=self.db, cuser=cuser)
        return service.auth_delete_user()


    @router_auth.put(path="/change_password/", status_code=status.HTTP_200_OK)
    async def change_password(
                            self,
                            data: UserChangePasswordBase,
                            cuser: UserModel = Depends(dependency.log_dependency)):
        service = AuthenticationService(db=self.db, cuser=cuser)
        return service.auth_change_password(data=data)


    @router_auth.post(path="/login/", status_code=status.HTTP_200_OK, response_model=TokenAccessRefreshBase)
    async def login(
                            self,
                            data: OAuth2PasswordRequestForm = Depends()):
        service = AuthenticationService(db=self.db)
        return service.auth_login(data=data)


    @router_auth.post(path="/refresh/", status_code=status.HTTP_200_OK, response_model=TokenAccessBase)
    async def refresh(
                            self,
                            cuser: UserModel = Depends(dependency.refresh_token_dependency)):
        service = AuthenticationService(db=self.db, cuser=cuser)
        return service.auth_refresh()


@cbv(router_blog)
class APIBlogClass:

    db: Session = Depends(get_db)


    @router_blog.post(path="/create_post/", status_code=status.HTTP_201_CREATED, response_model=PostViewBase)
    async def create_post(
                            self,
                            data: PostCreateBase = Form(),
                            cuser: UserModel = Depends(dependency.log_dependency),
                            request: Request = None):
        service = BlogService(db=self.db, cuser=cuser, request=request)
        return await service.blog_create_post(data=data)


    @router_blog.put(path="/update_post/{id}/", status_code=status.HTTP_200_OK, response_model=PostViewBase)
    async def update_post(
                            self,
                            id: int,
                            data: PostUpdateBase,
                            cuser: UserModel = Depends(dependency.log_dependency)):
        service = BlogService(db=self.db, cuser=cuser)
        return service.blog_update_post(id=id, data=data)


    @router_blog.delete(path="/delete_post/{id}/", status_code=status.HTTP_200_OK)
    async def delete_post(
                            self,
                            id: int,
                            cuser: UserModel = Depends(dependency.log_dependency)):
        service = BlogService(db=self.db, cuser=cuser)
        return service.blog_delete_post(id=id)


    @router_blog.get(path="/show_my_posts/", status_code=status.HTTP_200_OK, response_model=list[PostViewBase])
    async def show_my_posts(
                            self,
                            cuser: UserModel = Depends(dependency.log_dependency),
                            filter: PostOwnFilter = FilterDepends(PostOwnFilter)):
        service = BlogService(db=self.db, cuser=cuser)
        return service.blog_show_my_posts(filter=filter)


    @router_blog.get(path="/find_post/", status_code=status.HTTP_200_OK, response_model=list[PostViewBase])
    async def find_post(
                            self,
                            cuser: UserModel = Depends(dependency.log_dependency),
                            filter: PostFindFilter = FilterDepends(PostFindFilter)):
        service = BlogService(db=self.db, cuser=cuser)
        return service.blog_find_post(filter=filter)


    @router_blog.get(path="/download_file/{file_name}/", status_code=status.HTTP_200_OK)
    async def download_file(
                            self,
                            file_name: str,
                            cuser: UserModel = Depends(dependency.log_dependency)):
        service = BlogService(db=self.db, cuser=cuser)
        return service.blog_download_file(file_name=file_name)
