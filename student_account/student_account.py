from config_data.config import load_config
from schedule_parser import ScheduleParser
from rating_parser import RatingParser

from dataclasses import dataclass

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options

from async_property import async_property

from .exceptions import IncorrectDataException, AlreadyAuthorisedException
from selenium.common.exceptions import TimeoutException, NoSuchElementException


@dataclass
class StudentAccount:
    user_login: str

    user_pass: str

    url: str = "https://istudent.urfu.ru/?auth-ok"

    browser: webdriver.Remote = None

    @async_property
    async def driver(self):

        options = Options()

        config = load_config()

        # Загружаем настройки webdriver'а
        options._arguments.extend(config.webdriver.options)

        # Загружаем настройки Selenoid'а
        options._caps.update(config.webdriver.capability)

        # URL Selenoid-сервера
        SELENOID_URL = "http://localhost:4444/wd/hub"

        self.browser = webdriver.Remote(
            command_executor=SELENOID_URL,
            options=options
        )

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
            self.cookies = self.browser.get_cookies()
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
        return ScheduleParser(
            browser=self.browser,
            account=self
            )

    @property
    def rating(self):
        return RatingParser(
            cookies=self.cookies,
            account=self,
            browser=self.browser
            )
