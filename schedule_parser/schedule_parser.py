# Импорты необходимых библиотек
from itertools import zip_longest
from dataclasses import dataclass

# Для создания асинхронных свойств
from async_property import async_property

# Импорты библиотек selenium
from selenium.webdriver import Remote
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException

# Для парсинга HTML и работы с парсером lxml
from bs4 import BeautifulSoup, ResultSet, Tag
import lxml

# Импорт объекта для работы с таблицей расписания в БД
from database import WeeklySchedule


# Класс для обозначения отсутствия данных
class NoData:
    text = "Нет данных"


@dataclass
class ScheduleParser:
    """
    Класс для парсинга расписания студента.
    Использует Selenium для взаимодействия с сайтом и
    BeautifulSoup для извлечения данных.
    """
    browser: Remote                   # Экземпляр браузера Selenium WebDriver
    chat_id: int                      # id чата с пользователем
    schedule_table: WeeklySchedule    # Таблица с расписанием в БД

    # URL страницы с расписанием
    url: str = 'https://urfu.modeus.org/schedule-calendar'

    # Асинхронный метод, который парсит расписание.
    async def week_schedule(
            self, key: str, next_week: bool = False
    ) -> None:
        # Загрузка страницы с расписанием
        self.browser.get(self.url)

        self.browser.save_screenshot("screenshot.png")

        # Ожидание появления элементов на странице
        WebDriverWait(self.browser, 30).until(
            EC.visibility_of_any_elements_located(
                (By.CLASS_NAME, "fc-title")
            )
        )

        # Парсинг страницы с помощью BeautifulSoup
        soup = BeautifulSoup(self.browser.page_source, "lxml")

        # Если next_week == True,
        # загружаем расписание на следующую неделю
        if next_week:
            await self._change_to_next_week()

        week_days = [day.text for day in soup.select(".fc-day-header span")]

        # Выбираем колонку с расписанием для работы с определенным днём
        schedule_cols = soup.select(".fc-content-col")

        for day in week_days:

            day_schedule = self.get_day_schedule(
                day_num=week_days.index(day),
                schedule_cols=schedule_cols
            )

            for time, info in day_schedule.items():
                subject, location = info

                if key == "insert":
                    await self.insert_discipline_schedule(
                        week_day=week_days.index(day),
                        time_slot=time,
                        subject=subject,
                        location=location
                    )
                elif key == "update":
                    await self.update_disciplines_schedule(
                        week_day=week_days.index(day),
                        time_slot=time,
                        subject=subject,
                        location=location
                    )

    def get_day_schedule(
            self,
            schedule_cols: ResultSet[Tag],    # Колонки каждого дня недели
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

    # Асинхронный метод для вставки расписания в БД
    async def insert_discipline_schedule(
        self, week_day: int, time_slot: str, subject: str, location: str
    ) -> None:
        await self.schedule_table.insert_discipline(
            chat_id=self.chat_id,
            day_of_week=week_day,
            time_slot=time_slot,
            subject=subject,
            location=location
        )

    # Асинхронный метод для обновления расписания в БД
    async def update_disciplines_schedule(
        self, week_day: int, time_slot: str, subject: str, location: str
    ) -> None:
        await self.schedule_table.update_discipline(
            chat_id=self.chat_id,
            day_of_week=week_day,
            time_slot=time_slot,
            subject=subject,
            location=location
        )

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
