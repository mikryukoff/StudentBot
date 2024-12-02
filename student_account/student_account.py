# Импорты из локальных модулей
from config_data.config import load_config
from schedule_parser import ScheduleParser
from rating_parser import RatingParser

# Импорт инициализатора таблиц БД, словарь для хранения страниц и типы
from database import initialize_databases
from database import WeeklySchedule, Grades, Users

# Импорты стандартных библиотек
from dataclasses import dataclass

# Импорты из библиотеки Selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options

# Импорт асинхронного свойства
from async_property import async_property

# Импорты исключений из локальных и сторонних модулей
from .exceptions import IncorrectDataException, AlreadyAuthorisedException
from selenium.common.exceptions import TimeoutException, NoSuchElementException


@dataclass
class StudentAccount:
    user_login: str    # Логин пользователя
    user_pass: str     # Пароль пользователя
    chat_id: int       # id чата с пользователем

    # URL авторизации
    url: str = "https://istudent.urfu.ru/?auth-ok"

    # Асинхронное свойство, которое настраивает драйвер,
    # возвращает экземпляр класса StudentAccount
    @async_property
    async def driver(self):
        # Настройка опций браузера
        options = Options()
        config = load_config()

        # Настройки вебдрайвера
        options._arguments.extend(config.webdriver.options)

        # Настройки Selenoid
        options._caps.update(config.webdriver.capability)

        # Инициализация удаленного браузера
        self.browser = webdriver.Remote(
            command_executor=config.webdriver.selenoid_url,
            options=options
        )

        # Авторизация пользователя
        await self.__authorisation()
        await self.__connection_to_DB()

        return self

    # Асинхронный метод, который авторизует пользователя в Личном кабинете
    async def __authorisation(self) -> None:
        # Открытие страницы авторизации
        self.browser.get(self.url)

        try:
            # Кликаем по кнопке "Вход"
            self.browser.find_element(By.CLASS_NAME, "auth").click()

            # Ждём загрузки страницы авторизации
            WebDriverWait(self.browser, 10).until(
                EC.visibility_of_any_elements_located((By.ID, "userNameInput"))
            )

            # Вводим поля для авторизации и заходим на страницу
            self.browser.find_element(By.ID, "userNameInput").send_keys(self.user_login)
            self.browser.find_element(By.ID, "passwordInput").send_keys(self.user_pass)
            self.browser.find_element(By.ID, "submitButton").click()

            # Сохранение cookies
            self.cookies = self.browser.get_cookies()

        # Если страница не загрузилась, значит мы авторизованы
        except TimeoutException:
            raise AlreadyAuthorisedException

        try:

            # Проверка на правильность ввода данных
            self.browser.find_element(By.ID, "errorText")

        except NoSuchElementException:
            # Если ошибки нет, то всё верно
            pass

        else:

            # Если ошибка есть, то выходим из драйвера,
            # инициируем исключения неправильных данных
            self.browser.close()
            self.browser.quit()
            raise IncorrectDataException

    async def __connection_to_DB(self):
        tables = await initialize_databases()
        _, self.grades_table, self.schedule_table = tables

    # Свойство, которое возвращает экземпляр класса
    # ScheduleParser для работы с расписанием
    @property
    def schedule(self):
        # Создание экземпляра парсера расписания
        return ScheduleParser(
            browser=self.browser,
            chat_id=self.chat_id,
            schedule_table=self.schedule_table
        )

    # Свойство, которое возвращает экземпляр класса
    # RatingParser для работы с баллами
    @property
    def rating(self):
        # Создание экземпляра парсера рейтинга
        return RatingParser(
            browser=self.browser,
            chat_id=self.chat_id,
            grades_table=self.grades_table
        )
