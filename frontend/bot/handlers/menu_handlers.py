import bot.keyboards.menu_kb as kb
from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from bot.database import users_data
from bot.lexicon import LEXICON, LEXICON_COMMANDS

# Инициализация роутера
router: Router = Router()


# Обработчик команды "/start"
@router.message(CommandStart())
async def process_start_command(message: Message):
    # Отправляем приветственное сообщение и показываем меню входа
    await message.answer(
        text=LEXICON["/start"],
        reply_markup=kb.LogInMenu
    )

    # Инициализируем пустой словарь для данных пользователя, если его ещё нет
    users_data.setdefault(message.chat.id, {})


# Обработчик кнопки "В главное меню"
@router.message(F.text == LEXICON_COMMANDS["to_main_menu"])
async def main_menu_button(message: Message):
    # Отправляем сообщение и показываем главное меню
    await message.answer(
        text=LEXICON["to_main_menu"],
        reply_markup=kb.StartMenu
    )
