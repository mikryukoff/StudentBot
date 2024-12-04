# Импорты необходимых библиотек
from dataclasses import dataclass

# Импорты библиотек selenium
from selenium.webdriver import Remote
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains

# Для парсинга HTMLс использованием lxml
from bs4 import BeautifulSoup
import lxml

from database import Grades


@dataclass
class RatingParser:
    browser: Remote         # Экземпляр удаленного браузера (Selenium WebDriver)
    chat_id: int            # id чата с пользователем
    grades_table: Grades    # Таблица с баллами в БД

    # URL страницы с рейтингом дисциплин
    url: str = 'https://istudent.urfu.ru/s/http-urfu-ru-ru-students-study-brs?year=2024'    # CHANGE IN 2025

    # Метод для загрузки всех баллов по дисциплинам
    async def full_disciplines_rating(self, key: str):
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
        disciplines_names = [i.find_element(By.CLASS_NAME, "td-0").text.strip()
                             for i in disciplines]

        # zip-object с информацией по баллам и названием предмета
        disciplines_data = zip(
            soup.select(".rating-discipline-info.loaded"), disciplines_names
        )

        print(disciplines_names)

        # Сохраняем полный рейтинг для каждой дисциплины
        for discipline_rating, discipline_name in disciplines_data:

            components = []
            for chapter in discipline_rating.select('.mb-4:not([class*=" "])'):

                # Пропускаем пустые строки
                if not chapter.text:
                    continue

                score_data = chapter.find_all(
                    class_="discipline-inline-block"
                )

                for component in score_data:
                    name, score = " ".join(component.text.split()).split(":")
                    components.append((name, score))

            if key == "insert":

                await self.insert_disciplines_rating(
                    discipline_name=discipline_name,
                    components=components
                    )

            elif key == "update":

                await self.update_disciplines_rating(
                    discipline_name=discipline_name,
                    components=components
                )

    async def insert_disciplines_rating(
        self, discipline_name: str, components: list
    ) -> None:
        for component, score in components:
            await self.grades_table.insert_subject(
                chat_id=self.chat_id,
                subject=discipline_name,
                component=component,
                score=score
            )

    async def update_disciplines_rating(
        self, discipline_name: str, components: list
    ) -> None:
        for component, score in components:
            await self.grades_table.update_grades(
                chat_id=self.chat_id,
                subject=discipline_name,
                component=component,
                score=score
            )
