from dataclasses import dataclass
from fake_useragent import UserAgent

from environs import Env


# Описание настроек подключения к БД
@dataclass
class Database:
    host: str        # Хост БД
    user: str        #
    password: str    # Пароль от БД
    db_name: str     # Название БД


# Описание структуры для хранения пользовательских данных
@dataclass
class UserData:
    secret_key: str | bytes    # Секретный ключ пользователя


# Конфиг для настройки WebDriver
@dataclass
class WebDriver:
    options: list        # Список опций для настройки WebDriver
    capability: dict     # Возможности WebDriver (capabilities)
    selenoid_url: str    # URL для подключения к Selenoid


# Конфиг для настройки Telegram-бота
@dataclass
class TgBot:
    token: str


# Основной конфиг приложения
@dataclass
class Config:
    webdriver: WebDriver    # Конфигурация WebDriver
    tg_bot: TgBot           # Конфигурация Telegram-бота
    user_data: UserData     # Данные пользователя
    database: Database      # Данные для подключения к БД


# Функция загрузки конфигурации
def load_config(path: str | None = None) -> Config:
    # Инициализация окружения
    env = Env()
    env.read_env(path)

    # Настройки WebDriver
    options = [
        "--start-maximized",                                # Запуск браузера в режиме полного экрана
        "--disable-blink-features=AutomationControlled",    # Скрытие использования автоматизации
        "--no-sandbox",                                     # Отключение песочницы
        f'--user-agent={UserAgent().random}',               # Установка случайного user-agent
        '--enable-unsafe-swiftshader',                      # Включение SwiftShader
        '--disable-browser-side-navigation',                # Отключение навигации со стороны браузера
        "--disable-gpu",                                    # Отключение GPU
        "--headless"                                        # Запуск браузера в фоновом режиме (без UI)
    ]

    # Настройки для Selenoid
    capability = {
        "browserName": "chrome",      # Имя браузера
        "browserVersion": "128.0",    # Версия браузера
        "selenoid:options": {         # Специальные опции Selenoid
            "enableVNC": True,       # Включение VNC
            "enableVideo": False      # Отключение записи видео
        }
    }

    # Возврат конфигурации
    return Config(
        webdriver=WebDriver(
            options=options,                    # Установка опций WebDriver
            capability=capability,              # Установка возможностей WebDriver
            selenoid_url=env("SELENOID_URL")    # URL для подключения к Selenoid
        ),
        tg_bot=TgBot(token=env("BOT_TOKEN")),               # Токен Telegram-бота
        user_data=UserData(secret_key=env("SECRET_KEY")),   # Секретный ключ пользователя
        database=Database(
            host=env("DB_HOST"),            # Хост БД
            user=env("DB_USER"),            #
            password=env("DB_PASSWORD"),    # Пароль от БД
            db_name=env("DB_NAME")          # Название БД
        )
    )
