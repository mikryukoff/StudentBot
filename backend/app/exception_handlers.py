from uuid import uuid4

import app.exceptions as app_exc
from app.logger import log_error
from fastapi import status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import HTTPException
from fastapi.requests import Request
from fastapi.responses import JSONResponse


async def user_not_found_exc_handler(
    request: Request, exc: app_exc.UserNotFoundException
) -> JSONResponse:
    request_id = request.headers.get("X-Request_ID", str(uuid4()))

    await log_error(request, exc, status_code=exc.status_code, request_id=request_id)

    content = app_exc.UserNotFoundException(
        status_code=exc.status_code,
        detail=exc.detail,
        headers=exc.headers
    )

    return JSONResponse(
        status_code=exc.status_code,
        content=jsonable_encoder(content),
        headers={"X-Request_ID": request_id}
    )

#----------------------------------------------------------------------------------------#

async def invalid_credentials_handler(
    request: Request, exc: app_exc.InvalidCredentialsException
) -> JSONResponse:
    request_id = request.headers.get("X-Request_ID", str(uuid4()))

    await log_error(request, exc, status_code=exc.status_code, request_id=request_id)

    content = app_exc.InvalidCredentialsException(
        status_code=exc.status_code,
        detail=exc.detail,
        headers=exc.headers
    )

    return JSONResponse(
        status_code=exc.status_code,
        content=jsonable_encoder(content),
        headers={"X-Request_ID": request_id}
    )

async def validation_exception_handler(request: Request, exc: app_exc.ValidationException):
    request_id = request.headers.get("X-Request_ID", str(uuid4()))

    await log_error(request, exc, status_code=exc.status_code, request_id=request_id)

    content = app_exc.ValidationException(
        status_code=exc.status_code,
        detail=exc.detail
    )

    return JSONResponse(
        status_code=exc.status_code,
        content=jsonable_encoder(content),
        headers={"X-Request_ID": request_id}
    )

#----------------------------------------------------------------------------------------#

async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    request_id = request.headers.get("X-Request_ID", str(uuid4()))

    if isinstance(exc, HTTPException):
        status_code = exc.status_code
    else:
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    await log_error(request, exc, status_code=status_code, request_id=request_id)
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "status_code": status_code,
            "message": "Sorry, we have unexpected error on server.",
            "details": "Internal server error"
        },
        headers={"X-Request-ID": request_id}
    )