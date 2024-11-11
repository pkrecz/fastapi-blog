import os
import bcrypt
import uuid
from fastapi import Depends, UploadFile
from fastapi.security import OAuth2PasswordBearer
from fastapi.requests import Request
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
from config.settings import settings
from config.database import get_db
from jose import JWTError, jwt
from typing import IO
from . import exceptions
from .models import UserModel, PostModel, ImageModel
from .schemas import ImageBase


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/admin/login/")


class FunctionRepository:

    def query_get_user_by_username(self, db, username: str):
        return db.query(UserModel).filter_by(username=username)


    def query_get_user_by_email(self, db, email: str):
        return db.query(UserModel).filter_by(email=email)


    def query_get_post_by_user_id(self, db, user_id: int):
        return db.query(PostModel).filter_by(created_by=user_id)


    def query_get_post_by_title(self, db, title_post: str):
        return db.query(PostModel).filter_by(title=title_post)


    def query_get_post_own_by_ids(self, db, post_id: int, user_id: int):
        return db.query(PostModel).filter_by(id=post_id, created_by=user_id)


    def query_get_post_all(self, db):
        return db.query(PostModel)


    def check_the_same_password(self, password: str, password_confirm: str):
        return bool(password == password_confirm)


    def hash_password(self, password: str):
        pwd = password.encode("utf-8")
        salt = bcrypt.gensalt()
        return str(bcrypt.hashpw(password=pwd, salt=salt).decode("utf-8"))


    def verify_password(self, password: str, hashed_password: str):
        pwd = password.encode("utf-8")
        hashed_pwd = hashed_password.encode("utf-8")
        return bool(bcrypt.checkpw(password=pwd, hashed_password=hashed_pwd))


    def get_active_status(self, db, username: str):
        return bool(db.query(UserModel).filter_by(username=username).first().is_active)


    def authenticate_user(self, db, username: str, password: str):
        user_query = self.query_get_user_by_username(db, username=username)
        if user_query.count() == 0 or self.verify_password(password, user_query.first().hashed_password) == False:
            return False
        else:
            return user_query.first()


    def create_token(self, data: dict, refresh: bool):
        to_encode = data.copy()
        if refresh:
            expire = datetime.now(timezone.utc) + timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
            secret_key = settings.REFRESH_SECRET_KEY
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
            secret_key = settings.ACCESS_SECRET_KEY
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=settings.ALGORITHM)
        return str(encoded_jwt)


    def verify_token(self, token: str, refresh: bool):
        try:
            if refresh:
                payload = jwt.decode(token, settings.REFRESH_SECRET_KEY, algorithms=[settings.ALGORITHM])
            else:
                payload = jwt.decode(token, settings.ACCESS_SECRET_KEY, algorithms=[settings.ALGORITHM])
            username: str = payload.get("sub")
            if username is None:
                return None
            return username
        except jwt.ExpiredSignatureError:
            raise exceptions.TokenExpiredException
        except JWTError:
            return None


class DependencyRepository:

    async def log_dependency(self, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
        username = repo_functions.verify_token(token=token, refresh=False)
        if username is None:
            raise exceptions.CredentialsException
        user_query = repo_functions.query_get_user_by_username(db, username=username)
        if user_query.count() == 0:
            raise exceptions.CredentialsException
        if repo_functions.get_active_status(db, user_query.first().username) == False:
            raise exceptions.UserInActiveException
        return user_query.first()


    async def refresh_token_dependency(self, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
        username = repo_functions.verify_token(token=token, refresh=True)
        if username is None:
            raise exceptions.CredentialsException
        user_query = repo_functions.query_get_user_by_username(db, username=username)
        if user_query.count() == 0:
            raise exceptions.CredentialsException
        if repo_functions.get_active_status(db, user_query.first().username) == False:
            raise exceptions.UserInActiveException
        return user_query.first()


class MediaRepository:

    async def upload_files(self, files_to_upload: list[UploadFile], request: Request):
        list_of_files = []
        try:
            for file in files_to_upload:
                file_name = uuid.uuid4().hex
                file_extension = file.filename.split('.').pop()
                file_name_full = f"{file_name}.{file_extension}"
                file_path = os.path.join(settings.MEDIA_DIR, file_name_full)
                file_url = f"{str(request.base_url)[:-1]}{settings.MEDIA_URL}/{file_name_full}"
                file.file.seek(0)
                data = await file.read()
                with open(file_path, "wb") as buffer:
                    buffer.write(data)
                    buffer.close()
                list_of_files.append({
                                        "location" : str(file_url),
                                        "filename" : str(file_name_full),
                                        "size": int(file.size),
                                        "content_type": str(file.content_type)})
        except:
            raise exceptions.UploadFileException
        return list_of_files


    def validate_file_by_size(self, file: IO, max_size: int):
        real_file_size = 0
        for chunk in file.file:
            real_file_size += len(chunk)
            if real_file_size > max_size:
                raise exceptions.TooLargeFileException


    async def create_info_files(self, db, post_id: int, list_of_files: list):
        try:
            for file in list_of_files:
                ImageBase(**file)
                instance = ImageModel(**file, post_id=post_id)
                db.add(instance)
                db.commit()
        except:
            raise exceptions.BadRequestException("Error with saving info files.")


repo_functions = FunctionRepository()
repo_dependency = DependencyRepository()
repo_media = MediaRepository()
