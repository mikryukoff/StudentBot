from dataclasses import dataclass

from environs import Env


# Конфиг webvdriver'а
@dataclass
class WebDriver:
    user_profile: str
    # browser: str


@dataclass
class Config:
    webdriver: WebDriver


def load_config(path: str | None = None) -> Config:
    env = Env()
    env.read_env(path)

    return Config(
        webdriver=WebDriver(user_profile=env("USER_BROWSER_PROFILE"))
        )