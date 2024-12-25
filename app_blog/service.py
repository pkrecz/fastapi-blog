import os
from typing import TypeVar
from pydantic import BaseModel
from fastapi import status, Request
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import JSONResponse, FileResponse
from fastapi_filter.contrib.sqlalchemy import Filter
from sqlalchemy.orm import Session
from config.database import Base
from config.settings import settings
from . import exceptions
from .repository import AuthenticationRepository, BlogRepository, MediaRepository, CrudOperationRepository
from .models import UserModel, PostModel


media = MediaRepository()
Model = TypeVar("Model", bound=Base)


class AuthenticationService:

    def __init__(self, db: Session, cuser: str = None):
        self.db = db
        self.cuser = cuser
        self.model = UserModel
        self.auth = AuthenticationRepository(self.db, UserModel)
        self.crud = CrudOperationRepository(self.db, UserModel)
        self.blog = BlogRepository(self.db, PostModel)


    def auth_register_user(self, data: BaseModel) -> Model:
        if self.auth.check_if_exists_user_by_username(data.username):
            raise exceptions.UserExistsException
        if self.auth.check_if_exists_user_by_email(data.email):
            raise exceptions.EmailExistsException
        if self.auth.check_the_same_password(data.password, data.password_confirm) == False:
            raise exceptions.NotTheSamePasswordException
        input = {
            "username": data.username,
            "full_name": data.full_name,
            "email": data.email,
            "hashed_password": self.auth.hash_password(data.password)}
        return self.crud.create(input)


    def auth_update_user(self, data: BaseModel) -> Model:
        instance = self.auth.get_user_by_username(self.cuser.username)
        if not instance:
            raise exceptions.UserNotFoundException
        return self.crud.update(instance, data)


    def auth_delete_user(self):
        instance = self.auth.get_user_by_username(self.cuser.username)
        if not instance:
            raise exceptions.UserNotFoundException
        if self.blog.get_post_by_user_id(self.cuser.id):
            raise exceptions.BadRequestException("At least one post belongs to this user.")
        if not self.crud.delete(instance):
            raise
        return JSONResponse(content={"message": "User deleted successfully."}, status_code=status.HTTP_200_OK)


    def auth_change_password(self, data: BaseModel):
        instance = self.auth.get_user_by_username(self.cuser.username)
        if not instance:
            raise exceptions.UserNotFoundException
        if self.auth.check_the_same_password(data.new_password, data.new_password_confirm) == False:
            raise exceptions.NotTheSamePasswordException
        if self.auth.verify_password(data.old_password, instance.hashed_password) == False:
            raise exceptions.IncorrectPasswordException
        data = {"hashed_password": self.auth.hash_password(data.new_password)}
        self.crud.update(instance, data)
        return JSONResponse(content={"message": "Password changed successfully."}, status_code=status.HTTP_200_OK)


    def auth_login(self, data: OAuth2PasswordBearer):
        user = self.auth.authenticate_user(data.username, data.password)
        if not user:
            raise exceptions.CredentialsException
        if self.auth.get_active_status(user.username) == False:
            raise exceptions.UserInActiveException
        access_token = self.auth.create_token(data={"sub": user.username}, refresh=False)
        refresh_token = self.auth.create_token(data={"sub": user.username}, refresh=True)
        return JSONResponse(content={"access_token": access_token, "refresh_token": refresh_token}, status_code=status.HTTP_200_OK)


    def auth_refresh(self):
        access_token = self.auth.create_token(data={"sub": self.cuser.username}, refresh=False)
        return JSONResponse(content={"access_token": access_token}, status_code=status.HTTP_200_OK)


class BlogService:

    def __init__(self, db: Session, cuser: str = None, request: Request = None):
        self.db = db
        self.cuser = cuser
        self.request = request
        self.model = PostModel
        self.auth = AuthenticationRepository(self.db, PostModel)
        self.crud = CrudOperationRepository(self.db, PostModel)
        self.blog = BlogRepository(self.db, PostModel)


    async def blog_create_post(self, data: BaseModel):
        query = self.blog.query_get_post_by_title(data.title)
        instance = self.db.scalars(query).all()
        if instance:
            raise exceptions.BadRequestException("Post of this title already exists.")
        input = {**data.model_dump(exclude={"image"}), "created_by": self.cuser.id}
        instance = self.crud.create(input)
        if data.image:
            for file in data.image:
                media.validate_file_by_size(file, settings.MAX_FILE_SIZE)
            list_of_files = await media.upload_files(files_to_upload=data.image, request=self.request)
            await media.create_info_files(self.db, instance.id, list_of_files)
        return instance


    def blog_update_post(self, id: int, data: BaseModel):
        query = self.blog.query_get_post_own_by_ids(id, self.cuser.id)
        instance = self.db.scalar(query)
        if not instance:
            raise exceptions.NotFoundException("Post does not exists or is not yours.")
        return self.crud.update(instance, data)


    def blog_delete_post(self, id: int):
        query = self.blog.query_get_post_own_by_ids(id, self.cuser.id)
        instance = self.db.scalar(query)
        if not instance:
            raise exceptions.NotFoundException("Post does not exists or is not yours.")
        if not self.crud.delete(instance):
            raise
        return JSONResponse(content={"message": "Post deleted successfully."}, status_code=status.HTTP_200_OK)


    def blog_show_my_posts(self, filter: Filter):
        query = self.blog.query_get_post_by_user_id(self.cuser.id)
        if filter is not None:
            query = filter.filter(query)
            query = filter.sort(query)
        instance = self.db.scalars(query).all()
        if not instance:
            raise exceptions.NotFoundException("You do not have any post.")
        return instance


    def blog_find_post(self, filter: Filter):
        query = self.blog.query_get_post_all().join(UserModel)
        if filter is not None:
            query = filter.filter(query)
            query = filter.sort(query)
        instance = self.db.scalars(query).all()
        if not instance:
            raise exceptions.NotFoundException("Expected post was not found.")
        return instance


    def blog_download_file(self, file_name: str):
        location = os.path.join(os.getcwd(), settings.MEDIA_ROOT, file_name)
        if not os.path.exists(location):
            raise exceptions.NotFoundException("File was not found.")
        return FileResponse(
                                path=location,
                                media_type="application/octet-stream",
                                headers={"Content-Disposition": f"attachment; filename={file_name}"})
