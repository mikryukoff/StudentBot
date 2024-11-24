from aiogram.filters import BaseFilter
from aiogram.types import Message


class DateFilter(BaseFilter):
    def __init__(self):
        self.dates = ["пн.", "вт.", "ср.", "чт.", "пт.", "сб."]

    async def __call__(self, message: Message) -> bool:
        return message.text.split()[0] in self.dates


class DisciplineFilter(BaseFilter):
    def __init__(self, disciplines: list):
        self.disciplines = disciplines

    async def __call__(self, message: Message) -> bool:
        return message.text in self.disciplines
