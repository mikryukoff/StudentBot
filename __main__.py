from handlers import auth_handlers, rating_handlers, schedule_handlers, menu_handlers

import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from config_data.config import Config, load_config


logger = logging.getLogger(__name__)


async def main():

    logging.basicConfig(
        level=logging.INFO,
        format='%(filename)s:%(lineno)d #%(levelname)-8s '
               '[%(asctime)s] - %(name)s - %(message)s')

    logger.info('Starting bot')

    config: Config = load_config()

    # Инициализируем бот и диспетчер
    bot = Bot(
        token=config.tg_bot.token,
        default=DefaultBotProperties(link_preview_is_disabled=True)
    )
    dp = Dispatcher()

    # Регистриуем роутеры в диспетчере
    dp.include_router(menu_handlers.router)
    dp.include_router(auth_handlers.router)
    dp.include_router(schedule_handlers.router)
    dp.include_router(rating_handlers.router)

    # Пропускаем накопившиеся апдейты и запускаем polling
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


asyncio.run(main())
