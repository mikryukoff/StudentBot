from dataclasses import dataclass
import json
import re

from selenium.webdriver import Remote
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains

import asyncio
from aiohttp import ClientSession
from async_property import async_property

from bs4 import BeautifulSoup
import lxml


@dataclass
class RatingParser:
    cookies: dict

    browser: Remote

    account: None

    # URL страницы с расписанием.
    url: str = 'https://istudent.urfu.ru/s/http-urfu-ru-ru-students-study-brs'

    @async_property
    async def short_disciplines_rating(self) -> str:
        if not self._check_saved_file():
            await self.save_short_disciplines_rating()

        with open(r"database\rating.json", "r", encoding="utf-8") as json_file:
            rating = json.load(json_file)
            rating = rating[self.account.user_login]

            text = ""
            for discipline, score in rating.items():
                text += f"{discipline}: \n{score}\n\n"

            return text

    async def discipline_rating(self, discipline: str):
        if not self._check_full_saved_file():
            await self.save_full_disciplines_rating()

        with open(r"database\full_rating.json", "r", encoding="utf-8") as json_file:
            rating = json.load(json_file)
            rating = rating[self.account.user_login][discipline]

            text = f"{discipline}:\n"

            for i in rating:
                text += f"\n{i}:"
                scores = rating[i]
                for j in scores:
                    text += f"{j}:\n"
                    add_scores = "\n".join(re.split(r'(?=[А-Я])', scores[j].strip()))
                    text += f"{add_scores}\n"

            return text

    @async_property
    async def full_disciplines_rating(self):
        if not self._check_full_saved_file():
            await self.save_full_disciplines_rating()

        with open(r"database\full_rating.json", "r", encoding="utf-8") as json_file:
            rating = json.load(json_file)
            rating = rating[self.account.user_login]

            rating_iter = []

            text = ""
            for discipline in rating:
                text = f"{discipline}:\n"
                discipline_rating = rating[discipline]
                for i in discipline_rating:
                    text += f"\n{i}:"
                    scores = discipline_rating[i]
                    for j in scores:
                        text += f"{j}:\n"
                        add_scores = "\n".join(re.split(r'(?=[А-Я])', scores[j].strip()))
                        text += f"{add_scores}\n"

                rating_iter.append(text)

            return rating_iter

    async def save_short_disciplines_rating(self):
        async with ClientSession() as session:

            for cookie in self.cookies:
                session.cookie_jar.update_cookies({cookie["name"]: cookie["value"]})

            async with session.get(self.url) as response:
                soup = BeautifulSoup(await response.text(), "lxml")

        disciplines = soup.select(".rating-discipline:not(.not-actual)")

        with open(r"database\rating.json", "r", encoding="utf-8") as json_file:
            rating = json.load(json_file)

        with open(r"database\rating.json", "w", encoding="utf-8") as json_file:
            for i in disciplines:
                discipline, score = " ".join(i.text.split()[:-1]).split("Итоговая оценка:")
                rating.setdefault(self.account.user_login, {}).setdefault(discipline.strip(), score.strip())

            json.dump(rating, json_file, ensure_ascii=False, indent=2)

    async def save_full_disciplines_rating(self):
        self.browser.get(self.url)

        WebDriverWait(self.browser, 10).until(
            EC.visibility_of_any_elements_located((By.CLASS_NAME, "rating-discipline"))
        )

        actions = ActionChains(self.browser)

        disciplines = self.browser.find_elements(By.CSS_SELECTOR, ".rating-discipline:not(.not-actual)")

        for i in disciplines:
            actions.move_to_element(i).click(i).perform()

        soup = BeautifulSoup(self.browser.page_source, "lxml")

        disciplines_name = [i.find_element(By.CLASS_NAME, "td-0").text.strip() for i in disciplines]

        with open(r"database\full_rating.json", "r", encoding="utf-8") as json_file:
            rating = json.load(json_file)

        for discipline_rating, discipline_name in zip(soup.select(".rating-discipline-info.loaded"), disciplines_name):
            discipline_info = {}
            for chapter in discipline_rating.select('.mb-4:not([class*=" "])'):

                if not chapter.text:
                    continue

                chapter_name, chapter_rating = " ".join(chapter.find(class_="brs-h4").text.split()).split(":")
                full_info = " ".join(chapter.find(class_="rating-marks").text.split())

                discipline_info.setdefault(chapter_name, {}).setdefault(chapter_rating, full_info)

            rating.setdefault(self.account.user_login, {}).setdefault(discipline_name, discipline_info)

        with open(r"database\full_rating.json", "w", encoding="utf-8") as json_file:
            json.dump(rating, json_file, ensure_ascii=False, indent=2)

    def _check_saved_file(self) -> bool:
        try:
            with open(r"database\rating.json", "r", encoding="utf-8") as json_file:
                rating = json.load(json_file)
                if self.account.user_login in rating:
                    return True
                return False
        except FileNotFoundError:
            with open(r"database\rating.json", "w", encoding="utf-8") as json_file:
                json.dump(dict(), json_file, ensure_ascii=False, indent=2)
                return False

    def _check_full_saved_file(self) -> bool:
        try:
            with open(r"database\full_rating.json", "r", encoding="utf-8") as json_file:
                rating = json.load(json_file)
                if self.account.user_login in rating:
                    return True
                return False
        except FileNotFoundError:
            with open(r"database\full_rating.json", "w", encoding="utf-8") as json_file:
                json.dump(dict(), json_file, ensure_ascii=False, indent=2)
                return False
