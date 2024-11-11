from selenium.common.exceptions import TimeoutException, NoSuchElementException


class IncorrectDataException(NoSuchElementException):
    def __str__(self):
        return "Incorrect data, pls try again..."


class AlreadyAuthorisedException(TimeoutException):
    def __str__(self):
        return "User is already authorised."
