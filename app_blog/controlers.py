import os
from fastapi import APIRouter, status, Depends, Form, Request
from fastapi.responses import JSONResponse, FileResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_filter import FilterDepends
from sqlalchemy.orm import Session
from config.database import get_db
from config.settings import settings
from . import exceptions
from .repository import repo_functions, repo_dependency, repo_media
from .schemas import (UserCreateBase, UserViewBase, UserUpdateBase, UserChangePasswordBase,
                      TokenAccessRefreshBase, TokenAccessBase,
                      PostCreateBase, PostUpdateBase, PostViewBase)
from .models import UserModel, PostModel
from .filters import PostOwnFilter, PostFindFilter


router_user = APIRouter()
router_blog = APIRouter()


#  API for users
@router_user.post(path="/register/", status_code=status.HTTP_201_CREATED, response_model=UserViewBase)
async def register_user(
                            input_data: UserCreateBase,
                            db: Session = Depends(get_db)):
    try:
        user_query = repo_functions.query_get_user_by_username(db, input_data.username)
        if user_query.count() == 1:
            raise exceptions.UserExistsException
        user_query = repo_functions.query_get_user_by_email(db, input_data.email)
        if user_query.count() == 1:
            raise exceptions.EmailExistsException
        if repo_functions.check_the_same_password(input_data.password, input_data.password_confirm) == False:
            raise exceptions.NotTheSamePasswordException
        data = {
            "username": input_data.username,
            "full_name": input_data.full_name,
            "email": input_data.email,
            "hashed_password": repo_functions.hash_password(input_data.password)}
        instance = UserModel(**data)
        db.add(instance)
        db.commit()
        db.refresh(instance)
        return instance
    except Exception as exception:
        return JSONResponse(content={"detail": exception.detail}, status_code=exception.status_code)


@router_user.put(path="/update/", status_code=status.HTTP_200_OK, response_model=UserViewBase)
async def update_user(
                        input_data: UserUpdateBase,
                        db: Session = Depends(get_db),
                        current_user: UserModel = Depends(repo_dependency.log_dependency)):
    try:
        user_query = repo_functions.query_get_user_by_username(db, current_user.username)
        if user_query.count() == 0:
            raise exceptions.UserNotFoundException
        user_query.update(input_data.model_dump(exclude_unset=True))
        db.commit()
        return user_query.first()
    except Exception as exception:
        return JSONResponse(content={"detail": exception.detail}, status_code=exception.status_code)


@router_user.delete(path="/delete/", status_code=status.HTTP_200_OK)
async def delete_user(
                        db: Session = Depends(get_db),
                        current_user: UserModel = Depends(repo_dependency.log_dependency)):
    try:
        user_query = repo_functions.query_get_user_by_username(db, current_user.username)
        if user_query.count() == 0:
            raise exceptions.UserNotFoundException
        post_query = repo_functions.query_get_post_by_user_id(db, current_user.id)
        if post_query.count() != 0:
            raise exceptions.BadRequestException("At least one post belongs to this user.")
        db.delete(user_query.first())
        db.commit()
        return JSONResponse(content={"message": "User deleted successfully."}, status_code=status.HTTP_200_OK)
    except Exception as exception:
        return JSONResponse(content={"detail": exception.detail}, status_code=exception.status_code)


@router_user.put(path="/change_password/", status_code=status.HTTP_200_OK)
async def change_password(
                            input_data: UserChangePasswordBase,
                            db: Session = Depends(get_db),
                            current_user: UserModel = Depends(repo_dependency.log_dependency)):
    try:
        user_query = repo_functions.query_get_user_by_username(db, current_user.username)
        if user_query.count() == 0:
            raise exceptions.UserNotFoundException
        if repo_functions.check_the_same_password(input_data.new_password, input_data.new_password_confirm) == False:
            raise exceptions.NotTheSamePasswordException
        if repo_functions.verify_password(input_data.old_password, user_query.first().hashed_password) == False:
            raise exceptions.IncorrectPasswordException
        user_query.update({"hashed_password": repo_functions.hash_password(input_data.new_password)})
        db.commit()
        return JSONResponse(content={"message": "Password changed successfully."}, status_code=status.HTTP_200_OK)
    except Exception as exception:
        return JSONResponse(content={"detail": exception.detail}, status_code=exception.status_code)


@router_user.post(path="/login/", status_code=status.HTTP_200_OK, response_model=TokenAccessRefreshBase)
async def login(
                    form_data: OAuth2PasswordRequestForm = Depends(),
                    db: Session = Depends(get_db)):
    try:
        user = repo_functions.authenticate_user(db, form_data.username, form_data.password)
        if not user:
            raise exceptions.CredentialsException
        if repo_functions.get_active_status(db, user.username) == False:
            raise exceptions.UserInActiveException
        access_token = repo_functions.create_token(data={"sub": user.username}, refresh=False)
        refresh_token = repo_functions.create_token(data={"sub": user.username}, refresh=True)
        return JSONResponse(content={"access_token": access_token, "refresh_token": refresh_token}, status_code=status.HTTP_200_OK)
    except Exception as exception:
        return JSONResponse(content={"detail": exception.detail}, status_code=exception.status_code)


@router_user.post(path="/refresh/", status_code=status.HTTP_200_OK, response_model=TokenAccessBase)
async def refresh(
                    user: UserModel = Depends(repo_dependency.refresh_token_dependency)):
    try:
        access_token = repo_functions.create_token(data={"sub": user.username}, refresh=False)
        return JSONResponse(content={"access_token": access_token}, status_code=status.HTTP_200_OK)
    except Exception as exception:
        return JSONResponse(content={"detail": exception.detail}, status_code=exception.status_code)


#  API for blog
@router_blog.post(path="/create_post/", status_code=status.HTTP_201_CREATED, response_model=PostViewBase)
async def create_post(
                        input_data: PostCreateBase = Form(),
                        db: Session = Depends(get_db),
                        current_user: UserModel = Depends(repo_dependency.log_dependency),
                        request: Request = None):
    try:
        checkpoint = 0
        post_query = repo_functions.query_get_post_by_title(db, input_data.title)
        if post_query.count() != 0:
            raise exceptions.BadRequestException("Post of this title already exists.")
        instance = PostModel(**input_data.model_dump(exclude={"image"}), created_by=current_user.id)
        db.add(instance)
        db.commit()
        db.refresh(instance)
        checkpoint = 1
        if input_data.image:
            for file in input_data.image:
                repo_media.validate_file_by_size(file, settings.MAX_FILE_SIZE)
            list_of_files = await repo_media.upload_files(files_to_upload=input_data.image, request=request)
            await repo_media.create_info_files(db, instance.id, list_of_files)
        return instance
    except Exception as exception:
        if checkpoint == 1:
            db.delete(instance)
            db.commit()
        return JSONResponse(content={"detail": exception.detail}, status_code=exception.status_code)


@router_blog.put(path="/update_post/{post_id}/", status_code=status.HTTP_200_OK, response_model=PostViewBase)
async def update_post(
                        post_id: int,
                        input_data: PostUpdateBase,
                        db: Session = Depends(get_db),
                        current_user: UserModel = Depends(repo_dependency.log_dependency)):
    try:
        post_query = repo_functions.query_get_post_own_by_ids(db, post_id, current_user.id)
        if post_query.count() == 0:
            raise exceptions.NotFoundException("Post does not exists or is not yours.")
        post_query.update(input_data.model_dump(exclude_unset=True))
        db.commit()
        return post_query.first()
    except Exception as exception:
        return JSONResponse(content={"detail": exception.detail}, status_code=exception.status_code)


@router_blog.delete(path="/delete_post/{post_id}/", status_code=status.HTTP_200_OK)
async def delete_post(
                        post_id: int,
                        db: Session = Depends(get_db),
                        current_user: UserModel = Depends(repo_dependency.log_dependency)):
    try:
        post_query = repo_functions.query_get_post_own_by_ids(db, post_id, current_user.id)
        if post_query.count() == 0:
            raise exceptions.NotFoundException("Post does not exists or is not yours.")
        db.delete(post_query.first())
        db.commit()
        return JSONResponse(content={"message": "Post deleted successfully."}, status_code=status.HTTP_200_OK)
    except Exception as exception:
        return JSONResponse(content={"detail": exception.detail}, status_code=exception.status_code)


@router_blog.get(path="/show_my_posts/", status_code=status.HTTP_200_OK, response_model=list[PostViewBase])
async def show_my_posts(
                            db: Session = Depends(get_db),
                            current_user: UserModel = Depends(repo_dependency.log_dependency),
                            filter_post: PostOwnFilter = FilterDepends(PostOwnFilter)):
    try:
        post_query = repo_functions.query_get_post_by_user_id(db, current_user.id)
        post_query = filter_post.filter(post_query)
        post_query = filter_post.sort(post_query)
        if post_query.count() == 0:
            raise exceptions.NotFoundException("You do not have any post.")
        return post_query.all()
    except Exception as exception:
        return JSONResponse(content={"detail": exception.detail}, status_code=exception.status_code)


@router_blog.get(path="/find_post/", status_code=status.HTTP_200_OK, response_model=list[PostViewBase])
async def find_post(
                        db: Session = Depends(get_db),
                        current_user: UserModel = Depends(repo_dependency.log_dependency),
                        filter_post: PostFindFilter = FilterDepends(PostFindFilter)):
    try:
        post_query = repo_functions.query_get_post_all(db).join(UserModel)
        post_query = filter_post.filter(post_query)
        post_query = filter_post.sort(post_query)
        if post_query.count() == 0:
            raise exceptions.NotFoundException("Expected post was not found.")
        return post_query.all()
    except Exception as exception:
        return JSONResponse(content={"detail": exception.detail}, status_code=exception.status_code)


@router_blog.get(path="/download_file/{file_name}/", status_code=status.HTTP_200_OK)
async def download_file(
                        file_name: str,
                        db: Session = Depends(get_db),
                        current_user: UserModel = Depends(repo_dependency.log_dependency)):
    try:
        location = os.path.join(os.getcwd(), settings.MEDIA_DIR, file_name)
        if not os.path.exists(location):
            raise exceptions.NotFoundException("File was not found.")
        return FileResponse(
                                path=location,
                                media_type="application/octet-stream",
                                headers={"Content-Disposition": f"attachment; filename={file_name}"})
    except Exception as exception:
        return JSONResponse(content={"detail": exception.detail}, status_code=exception.status_code)
