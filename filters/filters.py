from aiogram.filters import BaseFilter
from aiogram.types import Message


# Кастомный фильтр для проверки даты
class DateFilter(BaseFilter):
    def __init__(self):
        self.dates = ["пн.", "вт.", "ср.", "чт.", "пт.", "сб."]

    # Асинхронный метод вызова фильтра
    async def __call__(self, message: Message) -> bool:
        # Проверяем, что первое слово сообщения является одним из обозначений дней недели
        return message.text.split()[0] in self.dates


# Кастомный фильтр для проверки названий дисциплин
class DisciplineFilter(BaseFilter):
    def __init__(self, disciplines: list):
        # Список допустимых названий дисциплин
        self.disciplines = disciplines

    # Асинхронный метод вызова фильтра
    async def __call__(self, message: Message) -> bool:
        # Проверяем, что текст сообщения совпадает с одним из названий дисциплин
        return message.text in self.disciplines
