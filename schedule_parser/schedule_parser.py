# Импорты необходимых библиотек
import json
from itertools import zip_longest
from dataclasses import dataclass

# Для создания асинхронных свойств
from async_property import async_property

# Импорты библиотек selenium
from selenium.webdriver import Remote
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# Для парсинга HTML и работы с парсером lxml
from bs4 import BeautifulSoup
import lxml


# Класс для обозначения отсутствия данных
class NoData:
    text = "Нет данных"


@dataclass
class ScheduleParser:
    """
    Класс для парсинга расписания студента.
    Использует Selenium для взаимодействия с сайтом и BeautifulSoup для извлечения данных.
    """
    browser: Remote    # Экземпляр браузера Selenium WebDriver
    account: None      # Аккаунт пользователя (StudentAccount)

    # URL страницы с расписанием
    url: str = 'https://urfu.modeus.org/schedule-calendar'

    # Асинхронное свойство для получения расписания на следующую неделю.
    @async_property
    async def next_week_schedule(self) -> None:
        await self.week_schedule(next_week=True)

    # Асинхронный метод для получения расписания на определенный день.
    async def day_schedule(self, date: str, next_week: bool = False) -> str:
        # Проверяем, сохранен ли файл с расписанием
        if not self._check_saved_file():
            await self.save_week_schedule(next_week=next_week)

        # Чтение расписания из файла
        with open(r"database\schedule.json", mode="rb") as json_file:
            day_schedule = json.load(json_file)

            # Работаем с расписанием пользователя по логину и дате
            day_schedule = day_schedule[self.account.user_login][date]

            text = f"{date}:\n\n"
            for time in day_schedule:

                # Если по дате нет расписания, то выходной
                if not day_schedule[time]:
                    text += "Выходной"
                    return text

                lesson_name, classroom = day_schedule[time]
                text += f"{lesson_name}\n{classroom}\n\n"

        return text

    # Асинхронное свойство для получения расписания на неделю.
    @async_property
    async def week_schedule(self, next_week: bool = False) -> list:
        # Проверяем, сохранен ли файл с расписанием
        if not self._check_saved_file():
            await self.save_week_schedule(next_week=next_week)

        # Чтение расписания из файла
        with open(r"database\schedule.json", mode="rb") as json_file:
            schedule = json.load(json_file)

            # Работаем с расписанием пользователя по логину
            schedule = schedule[self.account.user_login]

            schedule_iter = []
            for day in schedule:
                if not schedule[day]:
                    continue

                text = f"{day}:\n\n"
                for time, lesson_name in schedule[day].items():
                    if not lesson_name:
                        continue

                    text += f"{time}:\n{lesson_name[0]}\n{lesson_name[1]}\n\n"
                schedule_iter.append(text)

        return schedule_iter

    # Асинхронный метод, который сохраняет расписание на неделю в файл schedule.json.
    async def save_week_schedule(self, next_week: bool = False) -> None:
        # Загрузка страницы с расписанием
        self.browser.get(self.url)

        # Ожидание появления элементов на странице
        WebDriverWait(self.browser, 10).until(
            EC.visibility_of_any_elements_located(
                (By.CSS_SELECTOR, ".fc-title")
            )
        )

        # Парсинг страницы с помощью BeautifulSoup
        self.soup = BeautifulSoup(self.browser.page_source, "lxml")

        # Если next_week == True,
        # загружаем расписание на следующую неделю
        if next_week:
            await self._change_to_next_week()

        with open(r"database\schedule.json", mode="r", encoding="utf-8") as json_file:
            schedule = json.load(json_file)

        # Обновление данных расписания
        with open(r"database\schedule.json", mode="w", encoding="utf-8") as json_file:
            # Сохраняем названия дней недели
            week_days = [day.text for day in self.soup.select(".fc-day-header span")]

            # Выбираем колонку с расписанием для работы с определенным днём
            schedule_cols = self.soup.select(".fc-content-col")

            for day in week_days:
                day_schedule = self.get_day_schedule(
                    day_num=week_days.index(day),
                    schedule_cols=schedule_cols
                )
                schedule.setdefault(
                    self.account.user_login, {}
                ).setdefault(day, day_schedule)

            # Сохранение расписания
            json.dump(schedule, json_file, ensure_ascii=False, indent=2)

    def get_day_schedule(
            self,
            schedule_cols: list[BeautifulSoup],    # Колонки каждого дня недели
            day_num: int                           # Номер дня недели
    ) -> dict:
        day_col = schedule_cols[day_num]
        subjects = day_col.select(".fc-title")
        classrooms = day_col.select("small")
        subjects_time = day_col.select(".fc-time span")

        day_schedule: dict = {}
        for subject, classroom, time in zip_longest(
            subjects, classrooms, subjects_time, fillvalue=NoData
        ):
            day_schedule.setdefault(
                time.text.zfill(13), (subject.text, classroom.text)
            )

        return day_schedule

    # Метод, который проверяет, существует ли файл с расписанием.
    def _check_saved_file(self) -> bool:
        try:
            with open(r"database\schedule.json", "r", encoding="utf-8") as json_file:
                schedule = json.load(json_file)

                # Если запись по логину есть, значит парсить не надо
                if self.account.user_login in schedule:
                    return True

                return False

        except FileNotFoundError:

            # Создаем пустой файл, если он отсутствует
            with open(r"database\schedule.json", "w", encoding="utf-8") as json_file:
                json.dump(dict(), json_file, ensure_ascii=False, indent=2)

                return False

    # Асинхронный метод, который переключает страницу с расписанием на следующую неделю
    async def _change_to_next_week(self) -> None:

        # Находим кнопку, которая открывает следуюущую неделю, кликаем
        self.browser.find_element(
            By.XPATH, "//span[@class='fc-icon fc-icon-right-single-arrow']"
        ).click()

        # Ждём полной загрузки расписания
        WebDriverWait(self.browser, 10).until(
            EC.visibility_of_all_elements_located(
                (By.CSS_SELECTOR, ".fc-title")
            )
        )
