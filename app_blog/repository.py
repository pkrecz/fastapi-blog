import os
import bcrypt
import uuid
from pydantic import BaseModel
from fastapi import UploadFile
from fastapi.security import OAuth2PasswordBearer
from fastapi.requests import Request
from fastapi_filter.contrib.sqlalchemy import Filter
from sqlalchemy import exists, select
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
from config.settings import settings
from config.database import Base
from jose import JWTError, jwt
from typing import IO, TypeVar, Annotated
from . import exceptions
from .models import ImageModel
from .schemas import ImageBase


Model = TypeVar("Model", bound=Base)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/admin/login/")


class AuthenticationRepository:

    def __init__(self, db: Session = None, model: Model = None):
        self.db = db
        self.model = model


    def check_if_exists_user_by_username(self, username: str) -> bool:
        query = select(self.model).filter_by(username=username)
        query = exists(query).select()
        return self.db.scalar(query)


    def check_if_exists_user_by_email(self, email: str) -> bool:
        query = select(self.model).filter_by(email=email)
        query = exists(query).select()
        return self.db.scalar(query)


    def get_user_by_username(self, username: str) -> str:
        query = select(self.model).filter_by(username=username)
        return self.db.scalar(query)


    def check_the_same_password(self, password: str, password_confirm: str) -> bool:
        return bool(password == password_confirm)


    def hash_password(self, password: str) -> str:
        pwd = password.encode("utf-8")
        salt = bcrypt.gensalt()
        return str(bcrypt.hashpw(password=pwd, salt=salt).decode("utf-8"))


    def verify_password(self, password: str, hashed_password: str) -> bool:
        pwd = password.encode("utf-8")
        hashed_pwd = hashed_password.encode("utf-8")
        return bool(bcrypt.checkpw(password=pwd, hashed_password=hashed_pwd))


    def get_active_status(self, username: str) -> bool:
        query = select(self.model).filter_by(username=username)
        return bool(self.db.scalar(query).is_active)


    def authenticate_user(self, username: str, password: str):
        instance = self.get_user_by_username(username=username)
        if instance and self.verify_password(password, instance.hashed_password) == True:
            return instance
        else:
            return False


    def create_token(self, data: dict, refresh: bool) -> str:
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


    def verify_token(self, token: str, refresh: bool) -> str:
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


class BlogRepository:

    def __init__(self, db: Session, model: Model):
        self.db = db
        self.model = model

    def get_post_by_user_id(self, user_id: int) -> Model:
        query = select(self.model).filter_by(created_by=user_id)
        return self.db.scalars(query).all()


    def query_get_post_by_user_id(self, user_id: int):
        return select(self.model).filter_by(created_by=user_id)


    def query_get_post_by_title(self, title_post: str):
        return select(self.model).filter_by(title=title_post)


    def query_get_post_own_by_ids(self, post_id: int, user_id: int):
        return select(self.model).filter_by(id=post_id, created_by=user_id)


    def query_get_post_all(self):
        return select(self.model)


class MediaRepository:

    async def upload_files(self, files_to_upload: list[UploadFile], request: Request):
        list_of_files = []
        try:
            for file in files_to_upload:
                file_name = uuid.uuid4().hex
                file_extension = file.filename.split('.').pop()
                file_name_full = f"{file_name}.{file_extension}"
                file_path = os.path.join(settings.MEDIA_ROOT, file_name_full)
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
                db.flush()
        except:
            raise exceptions.BadRequestException("Error with saving info files.")


class CrudOperationRepository:

    def __init__(self, db: Session, model: Model):
        self.db = db
        self.model = model


    def get_by_id(self, id: int) -> Model:
        return self.db.get(self.model, id)


    def get_all(self, filter: Filter = None) -> Model:
        query = select(self.model)
        if filter is not None:
            query = filter.filter(query)
            query = filter.sort(query)
        return self.db.scalars(query).all()


    def create(self, record: Model) -> Model:
        self.db.add(record)
        self.db.flush()
        self.db.refresh(record)
        return record


    def update(self, record: Model, data: Annotated[BaseModel, dict]) -> Model:
        if isinstance(data, BaseModel):
            data = data.model_dump(exclude_none=True)
        for key, value in data.items():
            setattr(record, key, value)
        self.db.merge(record)
        self.db.flush()
        self.db.refresh(record)
        return record


    def delete(self, record: Model) -> bool:
        if record is not None:
            self.db.delete(record)
            self.db.flush()
            return True
        else:
            return False


    def retrieve(self, record: Model) -> Model:
        return record


    def list(self, record: Model) -> list[Model]:
        return record
