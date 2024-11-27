import keyboards.menu_kb as kb

from config_data.config import load_config
from cipher import PassCipher

from database import users_data

from lexicon import LEXICON, LEXICON_COMMANDS

from student_account import StudentAccount
from student_account.exceptions import IncorrectDataException

from aiogram import F, Router
from aiogram.types import Message


router: Router = Router()
config = load_config()
cipher: PassCipher = PassCipher(config.user_data.secret_key)


@router.message(F.text == LEXICON_COMMANDS["authorisation"])
async def authorisation(message: Message):
    if users_data[message.chat.id]:
        await message.answer(
            text=LEXICON["already_auth"],
            reply_markup=kb.StartMenu
            )
        return

    await message.answer(text=LEXICON["log_in"])


@router.message(F.text.contains("@"))
async def login(message: Message):
    if users_data[message.chat.id]:
        await message.answer(text=LEXICON["already_auth"])
        return

    users_data[message.chat.id]["login"] = message.text

    await message.answer(text=LEXICON["pass_in"])


# СДЕЛАТЬ НОРМАЛЬНУЮ ПРОВЕРКУ
@router.message(
        lambda x: x.text not in LEXICON_COMMANDS.values() and "📌" not in x.text
        )
async def password(message: Message):

    if (not users_data[message.chat.id]["login"] or
       "@" not in users_data[message.chat.id]["login"]):

        await message.answer(LEXICON["incorrect_user_data"])
        return

    login = users_data[message.chat.id]["login"]
    password = message.text

    await message.answer(LEXICON["connecting_to_PA"])

    try:
        account = await StudentAccount(
            user_login=login,
            user_pass=password).driver

        users_data[message.chat.id]["data"] = {
            "account": account,
            "schedule": account.schedule,
            "rating": account.rating,
            "schedule_page": 0,
            "rating_page": 0
        }

    except IncorrectDataException:
        await message.answer(
            text=LEXICON["incorrect_user_data"],
            reply_markup=kb.LogInMenu
            )
        users_data[message.chat.id] = {}
    else:
        await message.answer(
            text=LEXICON["successful_connection"],
            reply_markup=kb.StartMenu
            )

        users_data[message.chat.id]["password"] = cipher.encrypt_password(message.text)
