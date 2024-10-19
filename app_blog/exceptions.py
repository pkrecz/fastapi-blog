from fastapi import HTTPException, status


class NotFoundException(HTTPException):
    def __init__(self, message):
        super().__init__(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=message)


class BadRequestException(HTTPException):
    def __init__(self, message):
        super().__init__(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=message)


class UserNotFoundException(HTTPException):
    def __init__(self):
        super().__init__(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail='User was not found.')


class UserInActiveException(HTTPException):
    def __init__(self):
        super().__init__(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail='User is inactive.')


class NotTheSamePasswordException(HTTPException):
    def __init__(self):
        super().__init__(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail='Passwords should be the same.')


class UserExistsException(HTTPException):
    def __init__(self):
        super().__init__(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail='Username already exists.')


class EmailExistsException(HTTPException):
    def __init__(self):
        super().__init__(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail='Email already exists.')


class IncorrectPasswordException(HTTPException):
    def __init__(self):
        super().__init__(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail='Incorrect password.')


class CredentialsException(HTTPException):
    def __init__(self):
        super().__init__(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail='Invalid authentication credentials.')


class TokenExpiredException(HTTPException):
    def __init__(self):
        super().__init__(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail='Token expired.')


class NoPermissionsException(HTTPException):
    def __init__(self):
        super().__init__(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail='You have not a permission to perform action.')
