from aiogram.filters import BaseFilter
from aiogram.types import Message

import asyncio


class DateFilter(BaseFilter):
    def __init__(self):
        self.dates = ["пн.", "вт.", "ср.", "чт.", "пт.", "сб."]

    async def __call__(self, message: Message) -> bool:
        return message.text.split()[0] in self.dates
