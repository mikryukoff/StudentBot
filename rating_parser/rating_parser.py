from dataclasses import dataclass
import json

import asyncio
from aiohttp import ClientSession, ClientResponse
from async_property import async_property

from bs4 import BeautifulSoup
import lxml


@dataclass
class RatingParser:
    cookies: dict

    account: None

    # URL страницы с расписанием.
    url: str = 'https://istudent.urfu.ru/s/http-urfu-ru-ru-students-study-brs'

    async def get_soup(self, response: ClientResponse) -> BeautifulSoup:
        '''
        Асинхронная функция, которая возвращает объект BeautifulSoup.

        Возвращает:
            BeautifulSoup - объект BeautifulSoup.
        '''
        return BeautifulSoup(await response.text(), "lxml")

    @async_property
    async def all_disciplines_rating(self) -> str:
        if not self._check_saved_file():
            await self.save_disciplines_rating()

        with open(r"rating_parser\rating.json", "r", encoding="utf-8") as json_file:
            rating = json.load(json_file)
            rating = rating[self.account.user_login]

            text = ""
            for discipline, score in rating.items():
                text += f"{discipline}: \n{score}\n\n"

            return text

    async def save_disciplines_rating(self):
        async with ClientSession() as session:

            for cookie in self.cookies:
                session.cookie_jar.update_cookies({cookie["name"]: cookie["value"]})

            async with session.get(self.url) as response:
                soup = await self.get_soup(response=response)

                disciplines = soup.find_all("a", class_="rating-discipline")
                disciplines = filter(lambda x: "not-actual" not in x.get("class", ""), disciplines)

        with open(r"rating_parser\rating.json", "r", encoding="utf-8") as json_file:
            rating = json.load(json_file)

        with open(r"rating_parser\rating.json", "w", encoding="utf-8") as json_file:
            for i in disciplines:
                discipline, score = " ".join(i.text.split()[:-1]).split("Итоговая оценка:")
                rating.setdefault(self.account.user_login, {}).setdefault(discipline.strip(), score.strip())

            json.dump(rating, json_file, ensure_ascii=False, indent=2)

    def _check_saved_file(self) -> bool:
        try:
            with open(r"rating_parser\rating.json", "r", encoding="utf-8") as json_file:
                rating = json.load(json_file)
                if self.account.user_login in rating:
                    return True
                return False
        except FileNotFoundError:
            with open(r"rating_parser\rating.json", "w", encoding="utf-8") as json_file:
                json.dump(dict(), json_file, ensure_ascii=False, indent=2)
                return False
