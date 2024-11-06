from bot_config import BOT_TOKEN
from student_account import StudentAccount
from exceptions import IncorrectDataException

import keyboards as kb
from pagination_kb import create_pagination_keyboard

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery


bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

users_chat_id: dict = {}


# Команда "/start"
@dp.message(CommandStart())
async def process_start_command(message: Message):
    await message.answer("Привет!\nМеня зовут StudentBot!\nЯ могу отправить расписание и баллы БРС!")
    await message.answer("Для работы со мной, требуется авторизация по паролю и логину.", reply_markup=kb.LogInMenu)

    global users_chat_id
    users_chat_id.setdefault(message.chat.id, None)


@dp.message(F.text == "📅 Расписание")
async def send_schedule(message: Message):
    global users_chat_id
    global schedule
    global week_days

    await message.answer("Обрабатываю запрос...")

    schedule = await users_chat_id[message.chat.id]["schedule"].week_schedule
    week_days = [i.split("\n\n")[0].strip(":") for i in schedule]
    page = users_chat_id[message.chat.id]["page"]

    if page != len(week_days) - 1 and page != 0:

        await message.answer(
            text=schedule[page],
            reply_markup=create_pagination_keyboard("backward", week_days[page], "forward")
            )

    elif page == 0:

        await message.answer(
            text=schedule[page], 
            reply_markup=create_pagination_keyboard(week_days[page], "forward")
            )
    else:

        await message.answer(
            text=schedule[page], 
            reply_markup=create_pagination_keyboard("backward", week_days[page])
            )


@dp.callback_query(F.data == "forward")
async def press_forward(callback: CallbackQuery):
    global users_chat_id
    global schedule
    global week_days

    page = users_chat_id[callback.from_user.id]["page"]

    if page + 1 < len(week_days) - 1:

        await callback.message.edit_text(
            text=schedule[page + 1],
            reply_markup=create_pagination_keyboard("backward", week_days[page + 1], "forward")
            )
    else:

        await callback.message.edit_text(
            text=schedule[page + 1],
            reply_markup=create_pagination_keyboard("backward", week_days[page + 1])
            )

    users_chat_id[callback.from_user.id]["page"] += 1

    await callback.answer()


@dp.callback_query(F.data == "backward")
async def press_backward(callback: CallbackQuery):
    global users_chat_id
    global schedule
    global week_days

    page = users_chat_id[callback.from_user.id]["page"]

    if page - 1 > 0:

        await callback.message.edit_text(
            text=schedule[page - 1],
            reply_markup=create_pagination_keyboard("backward", week_days[page - 1], "forward")
            )

    else:

        await callback.message.edit_text(
            text=schedule[page - 1],
            reply_markup=create_pagination_keyboard(week_days[page - 1], "forward")
            )

    users_chat_id[callback.from_user.id]["page"] -= 1

    await callback.answer()


@dp.message(F.text == "📉 Баллы БРС")
async def send_rating(message: Message):
    global users_chat_id

    msg = await message.answer("Обрабатываю запрос...")

    rating = await users_chat_id[message.chat.id]["rating"].all_disciplines_rating

    await msg.edit_text(rating)


@dp.message(F.text == "✅ Авторизация")
async def authorisation(message: Message):
    global users_chat_id

    if users_chat_id[message.chat.id]:
        await message.answer("Вы уже авторизованы!")
        return

    await message.answer("Введите логин от личного кабинета: ")


@dp.message(F.text.contains("@"))
async def login(message: Message):
    global users_chat_id

    if users_chat_id[message.chat.id]:
        await message.answer("Попытка ввода логина...\nВы уже авторизованы!")
        return

    users_chat_id[message.chat.id] = message.text

    await message.answer("Введите пароль от личного кабинета: ")


# СДЕЛАТЬ НОРМАЛЬНУЮ ПРОВЕРКУ
@dp.message()
async def password(message: Message):
    global users_chat_id

    if not users_chat_id[message.chat.id] or "@" not in users_chat_id[message.chat.id]:
        await message.answer("Неверный логин! Повторите попытку: ")
        return

    if isinstance(users_chat_id[message.chat.id], dict):
        await message.answer("Попытка ввода пароля...\nВы уже авторизованы!")
        return

    login = users_chat_id[message.chat.id]
    password = message.text

    await message.answer("Подключаюсь к вашему личному кабинету...")

    try:
        account = await StudentAccount(login, password).driver

        users_chat_id[message.chat.id] = {
            "account": account,
            "schedule": account.schedule,
            "rating": account.rating,
            "page": 0
        }

    except IncorrectDataException:
        await message.answer("Неправильно введены данные, попробуйте ещё раз...", reply_markup=kb.LogInMenu)
        users_chat_id[message.chat.id] = None
    else:
        await message.answer("Подключение прошло успешно!", reply_markup=kb.StartMenu)


if __name__ == "__main__":
    dp.run_polling(bot)
