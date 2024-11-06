import json
from datetime import datetime
from itertools import zip_longest
from dataclasses import dataclass

import asyncio
from async_property import async_property

from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from bs4 import BeautifulSoup
import lxml


class NoData:
    text = "Нет данных"


@dataclass
class ScheduleParser:
    browser: Chrome

    account: None

    # Дата для получения расписания в определенный день.
    date: datetime = None

    # URL страницы с расписанием.
    url: str = 'https://urfu.modeus.org/schedule-calendar'

    @async_property
    async def next_week_schedule(self) -> None:
        '''
        Асинхронное свойство, которое возвращает расписание на следующую неделю.
        Обращается к асинхронному свойству ScheduleParser.week_schedule с аргументом next_week=True.
        '''
        await self.week_schedule(next_week=True)

    @async_property
    async def week_schedule(self, next_week: bool = False) -> list:
        '''
        BLANK
        '''
        if not self._check_saved_file():
            await self.save_week_schedule(next_week=next_week)
            self.browser.close()
            self.browser.quit()
            print(f"browser closed {self.account.user_login}")

        with open(r"schedule_parser\schedule.json", mode="rb") as json_file:
            schedule = json.load(json_file)
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

    async def save_week_schedule(self, next_week: bool = False) -> None:
        '''
        Сохраняет в файл schedule.json расписание на неделю,
        если расписание на эту неделю ранее не сохранялось, в формате:

            {
                Логин:
                {
                    день недели:
                    {
                        время 1-ой пары: [название предмета, аудитория],
                        ...,
                        время n-ой пары: [название предмета, аудитория]
                    }
                }
            }

        Параметры:
            next_week: bool - определяет, на какую неделю сохранять расписание.
                       True - сохраняет расписание на следующую неделю,
                       False - на текущую.
        '''
        self.browser.get(self.url)

        WebDriverWait(self.browser, 10).until(
            EC.visibility_of_any_elements_located((By.CSS_SELECTOR, ".fc-title"))
        )

        self.soup = BeautifulSoup(self.browser.page_source, "lxml")

        if next_week:
            await self._change_to_next_week()

        with open(r"schedule_parser\schedule.json", mode="r", encoding="utf-8") as json_file:
            schedule = json.load(json_file)

        # Записываем в файл schedule.json расписание.
        with open(r"schedule_parser\schedule.json", mode="w", encoding="utf-8") as json_file:
            week_days = [day.text for day in self.soup.select(".fc-day-header span")]
            schedule_cols = self.soup.select(".fc-content-col")

            for day in week_days:
                day_schedule = self.get_day_schedule(day_num=week_days.index(day), schedule_cols=schedule_cols)
                schedule.setdefault(self.account.user_login, {}).setdefault(day, day_schedule)

            json.dump(schedule, json_file, ensure_ascii=False, indent=2)

    def get_day_schedule(self, schedule_cols: list[BeautifulSoup], day_num: int) -> dict:
        '''
        По номеру дня недели возвращает полное расписание на день
        в виде словаря:

            {
                время 1-ой пары: (название предмета, аудитория),
                ...,
                время n-ой пары: (название предмета, аудитория)
            }

        Параметры:
            schedule_cols: list[BeautifulSoup] - список супов колонок дней с расписанием;
            day_num: int - номер дня недели (0 - пн., 1 - вт., ..., 6 - вс.).

        Возвращает:
            day_schedule: dict - словарь с расписанием на день (структура описана выше).
        '''
        # Колонка с расписанием на день.
        day_col = schedule_cols[day_num]

        subjects = day_col.select(".fc-title")
        classrooms = day_col.select("small")
        subjects_time = day_col.select(".fc-time span")

        # Если каких-то данных не достаёт, заполняем значением NoDataException,
        # то есть строкой "нет данных".
        day_schedule: dict = {}
        for subject, classroom, time in zip_longest(
            subjects, classrooms, subjects_time,
            fillvalue=NoData
        ):
            day_schedule.setdefault(time.text.zfill(13), (subject.text, classroom.text))

        return day_schedule

    def _check_saved_file(self) -> bool:
        try:
            with open(r"schedule_parser\schedule.json", "r", encoding="utf-8") as json_file:
                schedule = json.load(json_file)
                if self.account.user_login in schedule:
                    return True
                return False
        except FileNotFoundError:
            with open(r"schedule_parser\schedule.json", "w", encoding="utf-8") as json_file:
                json.dump(dict(), json_file, ensure_ascii=False, indent=2)
                return False

    async def _change_to_next_week(self) -> None:
        self.browser.find_element(By.XPATH, "//span[@class='fc-icon fc-icon-right-single-arrow']").click()

        WebDriverWait(self.browser, 10).until(
            EC.visibility_of_all_elements_located((By.CSS_SELECTOR, ".fc-title"))
        )

    def __str__(self):
        return f"ScheduleParser({self.account.user_login})"

    def __repr__(self):
        return f"ScheduleParser({self.account.user_login})"
