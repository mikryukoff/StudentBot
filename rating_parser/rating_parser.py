# Импорты необходимых библиотек
from dataclasses import dataclass
import json
import re

# Импорты библиотек selenium
from selenium.webdriver import Remote
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains

# Для работы с асинхронными HTTP-запросами
from aiohttp import ClientSession

# Для асинхронных свойств
from async_property import async_property

# Для парсинга HTMLс использованием lxml
from bs4 import BeautifulSoup
import lxml


@dataclass
class RatingParser:
    cookies: dict      # Словарь с cookies
    browser: Remote    # Экземпляр удаленного браузера (Selenium WebDriver)
    account: None      # Аккаунт пользователя (StudentAccount)

    # URL страницы с рейтингом дисциплин
    url: str = 'https://istudent.urfu.ru/s/http-urfu-ru-ru-students-study-brs'

    # Асинхронное свойство для получения рейтинга дисциплин (краткое)
    @async_property
    async def short_disciplines_rating(self) -> str:
        # Проверяем, если файл с рейтингом не найден, то сохраняем его
        if not self._check_saved_file():
            await self.save_short_disciplines_rating()

        # Загружаем данные из JSON файла
        with open(r"database\rating.json", "r", encoding="utf-8") as json_file:
            rating = json.load(json_file)

            # Работаем с рейтингом пользователя по логину
            rating = rating[self.account.user_login]

            # Формируем строку с рейтингом
            text = ""
            for discipline, score in rating.items():
                text += f"{discipline}: \n{score}\n\n"

            return text

    # Асинхронный метод для получения рейтинга по дисциплине
    async def discipline_rating(self, discipline: str):
        # Проверяем, если файл с рейтингом не найден, то сохраняем его
        if not self._check_full_saved_file():
            await self.save_full_disciplines_rating()

        # Загружаем полный рейтинг из файла
        with open(r"database\full_rating.json", "r", encoding="utf-8") as json_file:
            rating = json.load(json_file)

            # Работаем с рейтингом пользователя по логину
            rating = rating[self.account.user_login][discipline]

            text = f"{discipline}:\n"

            # Формируем текст с детализированным рейтингом
            for i in rating:
                text += f"\n{i}:"
                scores = rating[i]
                for j in scores:
                    text += f"{j}:\n"
                    add_scores = "\n".join(
                        re.split(r'(?=[А-Я])', scores[j].strip())  # Разделяем строки по заглавным буквам
                    )
                    text += f"{add_scores}\n"

            return text

    # Асинхронное свойство для получения полного рейтинга дисциплин
    @async_property
    async def full_disciplines_rating(self):
        # Проверяем, если файл с рейтингом не найден, то сохраняем его
        if not self._check_full_saved_file():
            await self.save_full_disciplines_rating()

        # Загружаем полный рейтинг из файла
        with open(r"database\full_rating.json", "r", encoding="utf-8") as json_file:
            rating = json.load(json_file)

            # Работаем с рейтингом пользователя по логину
            rating = rating[self.account.user_login]

            rating_iter = []
            text = ""

            # Формируем текст с полным рейтингом по всем дисциплинам
            for discipline in rating:
                text = f"{discipline}:\n"
                discipline_rating = rating[discipline]
                for i in discipline_rating:
                    text += f"\n{i}:"
                    scores = discipline_rating[i]
                    for j in scores:
                        text += f"{j}:\n"
                        add_scores = "\n".join(
                            re.split(r'(?=[А-Я])', scores[j].strip())  # Разделяем строки по заглавным буквам
                        )
                        text += f"{add_scores}\n"

                rating_iter.append(text)

            return rating_iter

    # Метод для сохранения краткого рейтинга дисциплин
    async def save_short_disciplines_rating(self):
        # Открываем асинхронную сессию для HTTP-запросов
        async with ClientSession() as session:

            # Добавляем cookies в сессию
            for cookie in self.cookies:
                session.cookie_jar.update_cookies(
                    {cookie["name"]: cookie["value"]}
                )

            # Получаем страницу с рейтингом
            async with session.get(self.url) as response:
                # Парсим HTML
                soup = BeautifulSoup(await response.text(), "lxml")

        # Получаем дисциплины с рейтингами
        disciplines = soup.select(".rating-discipline:not(.not-actual)")

        # Загружаем данные из файла и добавляем рейтинг
        with open(r"database\rating.json", "r", encoding="utf-8") as json_file:
            rating = json.load(json_file)

        # Сохраняем данные в файл
        with open(r"database\rating.json", "w", encoding="utf-8") as json_file:
            for i in disciplines:
                discipline, score = " ".join(
                    i.text.split()[:-1]
                ).split("Итоговая оценка:")

                rating.setdefault(
                    self.account.user_login, {}
                ).setdefault(discipline.strip(), score.strip())

            # Сохраняем обновленные данные
            json.dump(rating, json_file, ensure_ascii=False, indent=2)

    # Метод для сохранения полного рейтинга дисциплин
    async def save_full_disciplines_rating(self):
        # Загружаем страницу с помощью Selenium
        self.browser.get(self.url)

        # Ожидаем загрузки элементов страницы
        WebDriverWait(self.browser, 10).until(
            EC.visibility_of_any_elements_located(
                (By.CLASS_NAME, "rating-discipline")
            )
        )

        # Для выполнения действий в браузере
        actions = ActionChains(self.browser)

        # Получаем список дисциплин
        disciplines = self.browser.find_elements(
            By.CSS_SELECTOR,
            ".rating-discipline:not(.not-actual)"
        )

        # Осуществляем клики по каждой дисциплине
        for i in disciplines:
            actions.move_to_element(i).click(i).perform()

        # Получаем HTML-код страницы после кликов
        soup = BeautifulSoup(self.browser.page_source, "lxml")

        # Получаем названия дисциплин
        disciplines_name = [i.find_element(By.CLASS_NAME, "td-0").text.strip()
                            for i in disciplines]

        # Загружаем данные из файла для добавления полного рейтинга
        with open(r"database\full_rating.json", "r", encoding="utf-8") as json_file:
            rating = json.load(json_file)

            # zip-object с информацией по баллам и названием предмета
            discipline_data = zip(
                soup.select(".rating-discipline-info.loaded"), disciplines_name
            )

        # Сохраняем полный рейтинг для каждой дисциплины
        for discipline_rating, discipline_name in discipline_data:
            discipline_info = {}
            for chapter in discipline_rating.select('.mb-4:not([class*=" "])'):

                # Пропускаем пустые строки
                if not chapter.text:
                    continue

                chapter_name, chapter_rating = " ".join(
                    chapter.find(class_="brs-h4").text.split()
                ).split(":")

                full_info = " ".join(
                    chapter.find(class_="rating-marks").text.split()
                )

                discipline_info.setdefault(
                    chapter_name, {}
                ).setdefault(chapter_rating, full_info)

            rating.setdefault(
                self.account.user_login, {}
            ).setdefault(discipline_name, discipline_info)

        # Сохраняем обновленный полный рейтинг в файл
        with open(r"database\full_rating.json", "w", encoding="utf-8") as json_file:
            json.dump(rating, json_file, ensure_ascii=False, indent=2)

    # Метод для проверки наличия файла с краткой информацией по баллам
    def _check_saved_file(self) -> bool:
        try:
            with open(r"database\rating.json", "r", encoding="utf-8") as json_file:
                rating = json.load(json_file)

                # Если запись по логину есть, значит парсить не надо
                if self.account.user_login in rating:
                    return True

                return False

        except FileNotFoundError:

            # Если файл не найден, создаем новый
            with open(r"database\rating.json", "w", encoding="utf-8") as json_file:
                json.dump(dict(), json_file, ensure_ascii=False, indent=2)

                return False

    # Метод для проверки наличия файла с полной информацией по баллам
    def _check_full_saved_file(self) -> bool:
        try:
            with open(r"database\full_rating.json", "r", encoding="utf-8") as json_file:
                rating = json.load(json_file)

                # Если запись по логину есть, значит парсить не надо
                if self.account.user_login in rating:
                    return True

                return False

        except FileNotFoundError:

            # Если файл не найден, создаем новый
            with open(r"database\full_rating.json", "w", encoding="utf-8") as json_file:
                json.dump(dict(), json_file, ensure_ascii=False, indent=2)

                return False
