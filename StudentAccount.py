from parser_config import USER_BROWSER_PROFILE, USER_DATA_DIR
from schedule_parser.ScheduleParser import ScheduleParser

from dataclasses import dataclass
from time import sleep

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver import ChromeOptions

import asyncio
from async_property import async_property

from fake_useragent import UserAgent

from exceptions import IncorrectDataException, AlreadyAuthorisedException
from selenium.common.exceptions import SessionNotCreatedException, TimeoutException, NoSuchElementException


@dataclass
class StudentAccount:
    user_login: str

    user_pass: str

    __page_user_name: str = None

    url: str = "https://istudent.urfu.ru/?auth-ok"

    browser: webdriver.Chrome = None

    @async_property
    async def driver(self):

        # -------------------- Настройки Chrome Webdriver -------------------- #

        options = ChromeOptions()

        # Путь к директории профиля браузера Chrome.
        # options.add_argument(fr"{USER_DATA_DIR}")

        # Название директории профиля браузера Chrome.
        options.add_argument(f"--profile-directory={USER_BROWSER_PROFILE}")

        # Запуск браузера в полноэкранном режиме.
        options.add_argument("--start-maximized")

        # ЗАПОЛНИТЬ
        options.add_argument("--disable-blink-features=AutomationControlled")

        # Запуск браузера без графической оболочки.
        options.add_argument("--headless")

        # Отключение использования GPU.
        options.add_argument("--disable-gpu")

        options.add_argument("--no-sandbox")

        options.add_argument(f'--user-agent={UserAgent().random}')

        # options.add_argument('--disable-dev-shm-usage')

        options.add_argument('--enable-unsafe-swiftshader')

        options.add_argument('--disable-browser-side-navigation')

        options.binary_location = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

        # -------------------- Конец блока настроек Chrome Webdriver -------------------- #
        try:
            self.browser = webdriver.Chrome(options=options)
        except SessionNotCreatedException:
            sleep(1)
            self.browser = webdriver.Chrome(options=options)

        await self.__authorisation()

        return self

    async def __authorisation(self) -> None:
        self.browser.get(self.url)

        self.browser.find_element(By.CLASS_NAME, "auth").click()
        try:
            WebDriverWait(self.browser, 10).until(
                EC.visibility_of_any_elements_located((By.ID, "userNameInput"))
            )

            self.browser.find_element(By.ID, "userNameInput").send_keys(self.user_login)
            self.browser.find_element(By.ID, "passwordInput").send_keys(self.user_pass)
            self.browser.find_element(By.ID, "submitButton").click()
        except TimeoutException:
            raise AlreadyAuthorisedException

        try:
            self.browser.find_element(By.ID, "errorText")
        except NoSuchElementException:
            pass
        else:
            self.browser.close()
            self.browser.quit()
            raise IncorrectDataException

    @property
    def schedule(self):
        return ScheduleParser(browser=self.browser, account=self)
