from fastapi import APIRouter, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from config.database import get_db
from . import exceptions
from .repository import repo_functions, repo_dependency
from .schemas import (UserCreateBase, UserViewBase, UserUpdateBase, UserChangePasswordBase,
                      TokenAccessRefreshBase, TokenAccessBase,
                      PostCreateBase, PostUpdateBase, PostViewBase, PostAllBase)
from .models import UserModel, PostModel


router_user = APIRouter()
router_blog = APIRouter()


#  API for users
@router_user.post('/register/', status_code=status.HTTP_201_CREATED, response_model=UserViewBase)
async def register_user(input_data: UserCreateBase,
                        db: Session = Depends(get_db)):
    user_query = repo_functions.query_get_user_by_username(db, input_data.username)
    if user_query.count() == 1:
        raise exceptions.UserExistsException
    user_query = repo_functions.query_get_user_by_email(db, input_data.email)
    if user_query.count() == 1:
        raise exceptions.EmailExistsException
    if repo_functions.check_the_same_password(input_data.password, input_data.password_confirm) == False:
        raise exceptions.NotTheSamePasswordException
    data = {
        'username': input_data.username,
        'full_name': input_data.full_name,
        'email': input_data.email,
        'hashed_password': repo_functions.hash_password(input_data.password)}
    user_new = UserModel(**data)
    db.add(user_new)
    db.commit()
    db.refresh(user_new)
    return user_new


@router_user.put('/update/', status_code=status.HTTP_200_OK, response_model=UserViewBase)
async def update_user(input_data: UserUpdateBase,
                      db: Session = Depends(get_db),
                      current_user: UserModel = Depends(repo_dependency.log_dependency)):
    user_query = repo_functions.query_get_user_by_username(db, current_user.username)
    if user_query.count() == 0:
        raise exceptions.UserNotFoundException
    user_query.update(input_data.model_dump(exclude_unset=True))
    db.commit()
    return user_query.first()


@router_user.delete('/delete/', status_code=status.HTTP_200_OK)
async def delete_user(db: Session = Depends(get_db),
                      current_user: UserModel = Depends(repo_dependency.log_dependency)):
    user_query = repo_functions.query_get_user_by_username(db, current_user.username)
    if user_query.count() == 0:
        raise exceptions.UserNotFoundException
    post_query = repo_functions.query_get_post_by_user_id(db, current_user.id)
    if post_query.count() != 0:
        raise exceptions.BadRequestException('At least one post belongs to this user.')
    db.delete(user_query.first())
    db.commit()
    return {'message': 'User deleted successfully.'}


@router_user.put('/change_password/', status_code=status.HTTP_200_OK)
async def change_password(input_data: UserChangePasswordBase,
                            db: Session = Depends(get_db),
                            current_user: UserModel = Depends(repo_dependency.log_dependency)):
    user_query = repo_functions.query_get_user_by_username(db, current_user.username)
    if user_query.count() == 0:
        raise exceptions.UserNotFoundException
    if repo_functions.check_the_same_password(input_data.new_password, input_data.new_password_confirm) == False:
        raise exceptions.NotTheSamePasswordException
    if repo_functions.verify_password(input_data.old_password, user_query.first().hashed_password) == False:
        raise exceptions.IncorrectPasswordException
    user_query.update({'hashed_password': repo_functions.hash_password(input_data.new_password)})
    db.commit()
    return {'message': 'Password changed successfully.'}


@router_user.post('/login/', status_code=status.HTTP_200_OK, response_model=TokenAccessRefreshBase)
async def login(form_data: OAuth2PasswordRequestForm = Depends(),
                db: Session = Depends(get_db)):
    user = repo_functions.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise exceptions.CredentialsException
    if repo_functions.get_active_status(db, user.username) == False:
        raise exceptions.UserInActiveException
    access_token = repo_functions.create_token(data={'sub': user.username}, refresh=False)
    refresh_token = repo_functions.create_token(data={'sub': user.username}, refresh=True)
    return {'access_token': access_token, 'refresh_token': refresh_token}


@router_user.post('/refresh/', status_code=status.HTTP_200_OK, response_model=TokenAccessBase)
async def refresh(user: UserModel = Depends(repo_dependency.refresh_token_dependency)):
    access_token = repo_functions.create_token(data={'sub': user.username}, refresh=False)
    return {'access_token': access_token}


#  API for blog
@router_blog.post('/create_post/', status_code=status.HTTP_201_CREATED, response_model=PostViewBase)
async def create_post(post: PostCreateBase,
                      db: Session = Depends(get_db),
                      current_user: UserModel = Depends(repo_dependency.log_dependency)):
    post_query = repo_functions.query_get_post_by_title(db, post.title)
    if post_query.count() != 0:
        raise exceptions.BadRequestException('Post of this title already exists.')
    post_new = PostModel(**post.model_dump(), created_by=current_user.id)
    db.add(post_new)
    db.commit()
    db.refresh(post_new)
    return post_new


@router_blog.put('/update_post/{post_id}/', status_code=status.HTTP_200_OK, response_model=PostViewBase)
async def update_post(post_id: int,
                        input_data: PostUpdateBase,
                        db: Session = Depends(get_db),
                        current_user: UserModel = Depends(repo_dependency.log_dependency)):
    post_query = repo_functions.query_get_post_own_by_ids(db, post_id, current_user.id)
    if post_query.count() == 0:
        raise exceptions.NotFoundException('Post does not exists or is not yours.')
    post_query.update(input_data.model_dump(exclude_unset=True))
    db.commit()
    return post_query.first()


@router_blog.delete('/delete_post/{post_id}/', status_code=status.HTTP_200_OK)
async def delete_post(post_id: int,
                        db: Session = Depends(get_db),
                        current_user: UserModel = Depends(repo_dependency.log_dependency)):
    post_query = repo_functions.query_get_post_own_by_ids(db, post_id, current_user.id)
    if post_query.count() == 0:
        raise exceptions.NotFoundException('Post does not exists or is not yours.')
    db.delete(post_query.first())
    db.commit()
    return {'message': 'Post deleted successfully.'}


@router_blog.get('/show_my_posts/', status_code=status.HTTP_200_OK, response_model=list[PostAllBase])
async def show_my_posts(db: Session = Depends(get_db),
                        current_user: UserModel = Depends(repo_dependency.log_dependency)):
    post_query = repo_functions.query_get_post_by_user_id(db, current_user.id)
    if post_query.count() == 0:
        raise exceptions.NotFoundException('You do not have any post.')
    return post_query.all()
