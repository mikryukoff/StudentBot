from dataclasses import dataclass
from fake_useragent import UserAgent

from environs import Env


# Конфиг webvdriver'а
@dataclass
class WebDriver:
    options: list
    capability: dict
    selenoid_url: str


# Конфиг телеграм бота
@dataclass
class TgBot:
    token: str


@dataclass
class Config:
    webdriver: WebDriver
    tg_bot: TgBot


def load_config(path: str | None = None) -> Config:
    env = Env()
    env.read_env(path)

    # Настройки webdriver'а
    options = [
        "--start-maximized",
        "--disable-blink-features=AutomationControlled",
        "--no-sandbox",
        f'--user-agent={UserAgent().random}',
        '--enable-unsafe-swiftshader',
        '--disable-browser-side-navigation',
        # "--disable-gpu",
        # "--headless"
    ]

    # Настройки Selenoid'а
    capability = {
        "browserName": "chrome",
        "browserVersion": "128.0",
        "selenoid:options": {
            "enableVNC": True,
            "enableVideo": False,
        }
    }

    return Config(
        webdriver=WebDriver(
            options=options,
            capability=capability,
            selenoid_url=env("SELENOID_URL")
        ),
        tg_bot=TgBot(token=env("BOT_TOKEN"))
    )
