from dataclasses import dataclass
import json

import asyncio
from async_property import async_property

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from bs4 import BeautifulSoup
import lxml


@dataclass
class RatingParser:
    browser: None

    account: None

    # URL страницы с расписанием.
    url: str = 'https://istudent.urfu.ru/s/http-urfu-ru-ru-students-study-brs'

    @property
    def soup(self) -> BeautifulSoup:
        '''
        Свойство, которое возвращает объект BeautifulSoup.

        Возвращает:
            BeautifulSoup - объект BeautifulSoup.
        '''
        return BeautifulSoup(self.browser.page_source, "lxml")

    @async_property
    async def all_disciplines_rating(self) -> None:
        if not self._check_saved_file():
            await self.save_disciplines_rating()
            self.browser.close()
            self.browser.quit()
            print(f"browser closed {self.account.user_login}")

        with open(r"rating_parser\rating.json", "r", encoding="utf-8") as json_file:
            rating = json.load(json_file)
            rating = rating[self.account.user_login]

            text = ""
            for discipline, score in rating.items():
                text += f"{discipline}: \n{score}\n\n"

            return text

    async def save_disciplines_rating(self):
        self.browser.get(self.url)

        WebDriverWait(self.browser, 10).until(
            EC.visibility_of_element_located((By.ID, "disciplines"))
        )

        disciplines = self.soup.find("div", id="disciplines").find_all("div", recursive=False)
        disciplines = filter(lambda x: "display: none" not in x.get("style", ""), disciplines)

        with open(r"rating_parser\rating.json", "r", encoding="utf-8") as json_file:
            rating = json.load(json_file)

        with open(r"rating_parser\rating.json", "w", encoding="utf-8") as json_file:
            for i in disciplines:
                discipline, score = " ".join(i.text.split()[:-1]).split("Итоговая оценка:")
                rating.setdefault(self.account.user_login, {}).setdefault(discipline.strip(), score.strip())

            json.dump(rating, json_file, ensure_ascii=False, indent=2)

    def _check_saved_file(self) -> bool:
        try:
            with open(r"rating_parser\ratung.json", "r", encoding="utf-8") as json_file:
                rating = json.load(json_file)
                if self.account.user_login in rating:
                    return True
                return False
        except FileNotFoundError:
            with open(r"rating_parser\rating.json", "w", encoding="utf-8") as json_file:
                json.dump(dict(), json_file, ensure_ascii=False, indent=2)
                return False
