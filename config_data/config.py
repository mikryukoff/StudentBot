from dataclasses import dataclass

from environs import Env


# Конфиг webvdriver'а
@dataclass
class WebDriver:
    user_profile: str
    # browser: str


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

    return Config(
        webdriver=WebDriver(user_profile=env("USER_BROWSER_PROFILE")),
        tg_bot=TgBot(token=env("BOT_TOKEN"))
        )