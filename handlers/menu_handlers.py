from aiogram import F, Router
from lexicon import LEXICON, LEXICON_COMMANDS
from aiogram.types import Message
import keyboards.menu_kb as kb
from aiogram.filters import CommandStart
from database import users_data


router: Router = Router()


# Команда "/start"
@router.message(CommandStart())
async def process_start_command(message: Message):
    await message.answer(
        text=LEXICON["/start"],
        reply_markup=kb.LogInMenu
        )
    users_data.setdefault(message.chat.id, None)


@router.message(F.text == LEXICON_COMMANDS["to_main_menu"])
async def main_menu_button(message: Message):
    await message.answer(
        text=LEXICON["to_main_menu"],
        reply_markup=kb.StartMenu
        )
