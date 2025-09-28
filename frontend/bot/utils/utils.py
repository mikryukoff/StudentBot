import logging
import traceback
from typing import Any, Dict, Optional, Union

import aiohttp
import bot.exceptions.api_exceptions as api_exc
import bot.keyboards.menu_kb as kb
from bot.lexicon import LEXICON
from environs import Env

env = Env()
env.read_env()

logger = logging.getLogger(__name__)


async def make_api_request(
    url: str, 
    method: str = "GET", 
    params: Optional[Dict[str, Any]] = None,
    data: Optional[Union[Dict[str, Any], str, bytes, aiohttp.FormData]] = None,
    content_type: Optional[str] = None,
    headers: Optional[Dict[str, str]] = None
) -> Any:
    """Универсальная функция для запросов к API с поддержкой заголовков"""
    try:
        async with aiohttp.ClientSession() as session:
            request_kwargs = {}

            if params:
                request_kwargs["params"] = params
            
            # Обработка данных
            if data is not None:
                if content_type == "json" or (content_type is None and isinstance(data, dict)):
                    request_kwargs["json"] = data
                elif content_type == "form" or isinstance(data, aiohttp.FormData):
                    request_kwargs["data"] = data
                elif content_type == "text" or isinstance(data, str):
                    request_kwargs["text"] = data
                elif content_type == "binary" or isinstance(data, bytes):
                    request_kwargs["data"] = data
                else:
                    request_kwargs["json"] = data  # По умолчанию как JSON
            
            # Добавляем заголовки
            if headers:
                request_kwargs["headers"] = headers

            async with session.request(method, url, **request_kwargs) as response:
                
                if response.status == 200:
                    return await response.json()
                
                elif response.status == 404:
                    error_data = await response.json()
                    raise api_exc.UserNotFoundAPIException(404, error_data.get("detail", "User not found"))
                
                elif response.status == 401:
                    error_data = await response.json()
                    raise api_exc.InvalidCredentialsAPIException(401, error_data.get("detail", "Invalid credentials"))
                
                elif response.status == 422:
                    error_data = await response.json()
                    raise api_exc.ValidationAPIException(422, error_data.get("detail", "Validation error"))
                
                else:
                    error_text = await response.text()
                    raise api_exc.APIException(response.status, f"Server error: {error_text}")
                    
    except aiohttp.ClientError as e:
        raise api_exc.APIException(0, f"Network error: {str(e)}")


async def make_discipline_rating_request(
    user_id: int,
    method: str = "GET", 
    params: Optional[Dict[str, Any]] = None,
    data: Optional[Union[Dict[str, Any], str, bytes, aiohttp.FormData]] = None,
    content_type: Optional[str] = None,
    headers: Optional[Dict[str, str]] = None,
    query: bool = True
) -> Any:

    if query:
        request_url = f"{env("API_URL")}/disciplines/{user_id}/rating"
    else:
        request_url = f"{env("API_URL")}/disciplines/{user_id}"

    try:
        data = await make_api_request(
            request_url,
            method=method,
            params=params,  # Передаем query-параметры
            data=data,
            content_type=content_type,
            headers=headers
        )
        return True, data

    except api_exc.UserNotFoundAPIException:
        return False, {"text": "Авторизуйся", "reply_markup": kb.LogInMenu}

    except api_exc.APIException as e:
        logger.exception("APIException occurred")
        return False, {"text": LEXICON["error"]}


async def make_schedule_request(
    user_id: int,
    method: str = "GET", 
    params: Optional[Dict[str, Any]] = None,
    data: Optional[Union[Dict[str, Any], str, bytes, aiohttp.FormData]] = None,
    content_type: Optional[str] = None,
    headers: Optional[Dict[str, str]] = None,
) -> Any:

    request_url = f"{env('API_URL')}/schedule/{user_id}"

    try:
        data = await make_api_request(
            request_url,
            method=method,
            params=params,
            data=data,
            content_type=content_type,
            headers=headers
        )
        return True, data

    except api_exc.UserNotFoundAPIException:
        return False, {"text": "Авторизуйся", "reply_markup": kb.LogInMenu}

    except api_exc.APIException as e:
        print(traceback.format_exc())
        return False, {"text": LEXICON["error"]}
