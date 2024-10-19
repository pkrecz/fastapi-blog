import bcrypt
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
from config.settings import settings
from config.database import get_db
from jose import JWTError, jwt
from . import exceptions
from .models import UserModel, PostModel


oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/admin/login/')


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

    def check_the_same_password(self, password: str, password_confirm: str):
        return bool(password == password_confirm)
    
    def hash_password(self, password: str):
        pwd = password.encode('utf-8')
        salt = bcrypt.gensalt()
        return str(bcrypt.hashpw(password=pwd, salt=salt).decode('utf-8'))

    def verify_password(self, password: str, hashed_password: str):
        pwd = password.encode('utf-8')
        hashed_pwd = hashed_password.encode('utf-8')
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
        to_encode.update({'exp': expire})
        encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=settings.ALGORITHM)
        return str(encoded_jwt)

    def verify_token(self, token: str, refresh: bool):
        try:
            if refresh:
                payload = jwt.decode(token, settings.REFRESH_SECRET_KEY, algorithms=[settings.ALGORITHM])
            else:
                payload = jwt.decode(token, settings.ACCESS_SECRET_KEY, algorithms=[settings.ALGORITHM])
            username: str = payload.get('sub')
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


repo_functions = FunctionRepository()
repo_dependency = DependencyRepository()
