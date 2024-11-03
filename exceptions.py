from selenium.common.exceptions import TimeoutException


class NoSuchStudentFoundException(TimeoutException):
    def __str__(self):
        return f"Student: {self.msg} not found."


class AlreadyAuthorisedException(TimeoutException):
    def __str__(self):
        return "User is already authorised."
