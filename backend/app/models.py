from datetime import date
from typing import Annotated

from pydantic import BaseModel, Field


class UserBase(BaseModel):
    user_id: int

class User(UserBase):
    email: Annotated[str, Field(pattern=r"[a-zA-Z]+@[a-zA-Z]")]
    password: str

class UserInDB(UserBase):
    hashed_password: str
    week_start_date: date

#----------------------------------------------------------------------------------------#

class NotFoundExceptionModel(BaseModel):
    status_code: int

class UserNotFoundExceptionModel(NotFoundExceptionModel):
    detail: str | None
    headers: Annotated[dict[str, str] | None, Field(default=None)]

#----------------------------------------------------------------------------------------#

class InvalidDataExceptionModel(BaseModel):
    status_code: int

class InvalidCredentialsExceptionModel(InvalidDataExceptionModel):
    detail: str | None
    headers: Annotated[dict[str, str] | None, Field(default=None)]

class RequestValidationErrorModel(InvalidDataExceptionModel):
    detail: str | None
    headers: Annotated[dict[str, str] | None, Field(default=None)]