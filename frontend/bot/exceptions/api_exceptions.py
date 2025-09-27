class APIException(Exception):
    """Базовое исключение для ошибок API"""
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail
        super().__init__(f"API Error {status_code}: {detail}")

class UserNotFoundAPIException(APIException):
    """Пользователь не найден в API"""
    pass

class UnauthorizedAPIException(APIException):
    """Ошибка авторизации в API"""
    pass

class ValidationAPIException(APIException):
    """Ошибка валидации данных в API"""
    pass

class InvalidCredentialsAPIException(APIException):
    """Неверные данные для входа в ЛК"""
    pass
