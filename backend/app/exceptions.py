from typing import Any, Optional

from fastapi import HTTPException, status
from fastapi.exceptions import RequestValidationError


class NotFoundException(HTTPException):
    def __init__(self, detail: str = "Not Found", **kwargs: Any):
        kwargs["detail"] = detail
        kwargs["status_code"] = status.HTTP_404_NOT_FOUND
        super().__init__(**kwargs)

class UserNotFoundException(NotFoundException):
    def __init__(self, user_id: Optional[int] = None, **kwargs: Any):
        detail = f"User with id {user_id} doesn't exist." if user_id else "User not found"
        kwargs["detail"] = detail
        super().__init__(**kwargs)

#-----------------------------------------------------------------------------------------#

class AuthException(HTTPException):
    """Базовое исключение для ошибок аутентификации"""
    def __init__(self, detail: str = "Authentication error", **kwargs: Any):
        kwargs["detail"] = detail
        kwargs["status_code"] = status.HTTP_401_UNAUTHORIZED
        super().__init__(**kwargs)

class InvalidCredentialsException(AuthException):
    """Неверные учетные данные"""
    def __init__(self, detail: str = "Invalid email or password", **kwargs: Any):
        kwargs["detail"] = detail
        super().__init__(**kwargs)

#-----------------------------------------------------------------------------------------#

class ValidationException(RequestValidationError):
    def __init__(self, errors, *, body = None):
        super().__init__(errors, body=body)
        self.status_code = status.HTTP_422_UNPROCESSABLE_CONTENT
        self.detail = "Invalid input"
