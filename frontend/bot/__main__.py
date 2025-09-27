# Импорты локальных модулей
from bot.handlers import (
    auth_handlers,        # Хэндлеры для авторизации
    rating_handlers,      # Хэндлеры для рейтинга
    schedule_handlers,    # Хэндлеры для расписания
    menu_handlers         # Хэндлеры для меню
)

# Импорты стандартных библиотек
import asyncio
import logging

# Импорты из aiogram
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties

# Импорты конфигурации
from config import load_config

# Логгер для работы с логами
logger = logging.getLogger(__name__)


async def main():
    # Настройка логирования
    logging.basicConfig(
        level=logging.INFO,
        format='%(filename)s:%(lineno)d #%(levelname)-8s '
               '[%(asctime)s] - %(name)s - %(message)s'
    )

    logger.info('Starting bot')

    # Загрузка конфигурации
    config = load_config()

    # Инициализация бота и диспетчера
    bot = Bot(
        token=config.tg_bot.token,
        default=DefaultBotProperties(link_preview_is_disabled=True)
    )
    dp = Dispatcher()

    # Регистрация роутеров в диспетчере
    dp.include_router(schedule_handlers.router)
    dp.include_router(rating_handlers.router)
    dp.include_router(menu_handlers.router)
    dp.include_router(auth_handlers.router)

    # Удаление вебхуков и запуск long-polling
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:

        # Запуск асинхронного приложения
        asyncio.run(main())

    except (KeyboardInterrupt, SystemExit):

        # Логирование остановки бота
        logger.error("Bot stopped!")
