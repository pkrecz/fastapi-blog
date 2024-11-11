from fastapi import UploadFile
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional


# Schemas for users
class UserBase(BaseModel):
    username: str
    email: EmailStr


class UserViewBase(BaseModel):
    id: int
    username: str
    full_name: str
    email: EmailStr
    is_active: bool


class UserCreateBase(BaseModel):
    username: str
    full_name: str
    email: EmailStr
    password: str
    password_confirm: str


class UserUpdateBase(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None


class UserChangePasswordBase(BaseModel):
    old_password: str
    new_password: str
    new_password_confirm: str


# Schemas for token
class TokenAccessRefreshBase(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenAccessBase(BaseModel):
    access_token: str
    token_type: str = "bearer"


# Schemas for images
class ImageBase(BaseModel):
    location: str
    filename: str
    size: int
    content_type: str


# Schemas for posts
class PostCreateBase(BaseModel):
    title: str
    content: str
    image: Optional[list[UploadFile]] | None = None


class PostUpdateBase(BaseModel):
    content: Optional[str] = None
    published: Optional[bool] = None


class PostViewBase(BaseModel):
    id: int
    title: str
    content: str
    published: bool
    created_at: datetime
    users: UserBase
    images: list[ImageBase]
