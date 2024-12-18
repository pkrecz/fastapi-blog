from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import Type, TypeVar
from config.database import Base, get_db
from . import exceptions
from .models import UserModel
from .repository import AuthenticationRepository


Model = TypeVar("Model", bound=Base)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/admin/login/")


class Dependency:


    async def log_dependency(
                                        self,
                                        token: str = Depends(oauth2_scheme),
                                        db: Session = Depends(get_db)) -> Type[Model]:
        self.auth = AuthenticationRepository(db, UserModel)
        username = self.auth.verify_token(token=token, refresh=False)
        if username is None:
            raise exceptions.CredentialsException
        instance = self.auth.get_user_by_username(username)
        if self.auth.get_active_status(instance.username) == False:
            raise exceptions.UserInActiveException
        return instance


    async def refresh_token_dependency(
                                        self,
                                        token: str = Depends(oauth2_scheme),
                                        db: Session = Depends(get_db)) -> Type[Model]:
        self.auth = AuthenticationRepository(db, UserModel)
        username = self.auth.verify_token(token=token, refresh=True)
        if username is None:
            raise exceptions.CredentialsException
        instance = self.auth.get_user_by_username(username=username)
        if self.auth.get_active_status(instance.username) == False:
            raise exceptions.UserInActiveException
        return instance
