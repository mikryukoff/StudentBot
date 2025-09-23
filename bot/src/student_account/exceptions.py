# Импорты необходимых исключений из библиотеки Selenium
from selenium.common.exceptions import TimeoutException, NoSuchElementException


class IncorrectDataException(NoSuchElementException):
    """
    Исключение для случаев, когда предоставлены некорректные данные.

    Наследуется от Selenium.NoSuchElementException, что позволяет
    использовать его в контексте отсутствия элементов на странице.
    """
    def __str__(self):
        """
        Возвращает строковое представление исключения.
        """
        return "Incorrect data, pls try again..."


class AlreadyAuthorisedException(TimeoutException):
    """
    Исключение для случаев, когда пользователь уже авторизован.

    Наследуется от Selenium.TimeoutException, так как связано с ожиданием.
    """
    def __str__(self):
        """
        Возвращает строковое представление исключения.
        """
        return "User is already authorised."
