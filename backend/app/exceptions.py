from typing import Any, Optional

from fastapi import HTTPException, status
from fastapi.exceptions import RequestValidationError


class NotFoundException(HTTPException):
    def __init__(self, detail: str = "Not Found", **kwargs: Any):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail, **kwargs)

class UserNotFoundException(NotFoundException):
    def __init__(self, user_id: Optional[int] = None, **kwargs: Any):
        detail = f"User with id {user_id} doesn't exist." if user_id else "User not found"
        super().__init__(detail=detail, **kwargs)

#-----------------------------------------------------------------------------------------#

class AuthException(HTTPException):
    """Базовое исключение для ошибок аутентификации"""
    def __init__(self, detail: str = "Authentication error", **kwargs: Any):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            **kwargs
        )

class InvalidCredentialsException(AuthException):
    """Неверные учетные данные"""
    def __init__(self, detail: str = "Invalid email or password"):
        super().__init__(detail=detail)

#-----------------------------------------------------------------------------------------#

class ValidationException(RequestValidationError):
    def __init__(self, errors, *, body = None):
        super().__init__(errors, body=body)
        self.status_code = status.HTTP_422_UNPROCESSABLE_CONTENT
        self.detail = "Invalid input"