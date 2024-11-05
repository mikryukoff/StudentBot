from bot_config import BOT_TOKEN
from student_account import StudentAccount
from exceptions import IncorrectDataException

import keyboards as kb

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message


bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

users_chat_id: dict = {}


# Команда "/start"
@dp.message(Command(commands=["start"]))
async def process_start_command(message: Message):
    await message.answer("Привет!\nМеня зовут ScheduleBot!\nЯ могу отправить расписание!")
    await message.answer("Для работы со мной, требуется авторизация по паролю и логину.", reply_markup=kb.LogInMenu)

    global users_chat_id
    users_chat_id.setdefault(message.chat.id, None)


# Меню "Расписание"
@dp.message(F.text == "📅 Расписание")
async def send_schedule(message: Message):
    global users_chat_id

    msg = await message.answer("Обрабатываю запрос...")
    # current_user_name = users_chat_id[message.chat.id][0]

    schedule = await users_chat_id[message.chat.id][1].schedule.week_schedule

    await msg.edit_text(schedule[0])
    del schedule[0]

    for text in schedule:
        await message.answer(text)


# Меню "Баллы БРС"
@dp.message(F.text == "📉 Баллы БРС")
async def send_rating(message: Message):
    global users_chat_id

    msg = await message.answer("Обрабатываю запрос...")

    rating = await users_chat_id[message.chat.id][1].rating.all_disciplines_rating

    await msg.edit_text(rating)


@dp.message(F.text == "✅ Авторизация")
async def authorisation(message: Message):
    await message.answer("Введите логин от личного кабинета: ")


@dp.message(lambda message: "@" in message.text)
async def login(message: Message):
    global users_chat_id

    users_chat_id[message.chat.id] = message.text

    await message.answer("Введите пароль от личного кабинета: ")


@dp.message()
async def password(message: Message):
    global users_chat_id

    if not users_chat_id[message.chat.id]:
        await message.answer("Неверный логин! Повторите попытку: ")
        return

    if isinstance(users_chat_id[message.chat.id], tuple):
        await message.answer("Вы уже авторизованы!")
        return

    if "@" not in users_chat_id[message.chat.id]:
        await message.answer("Неверный логин! Повторите попытку: ")
        return

    login = users_chat_id[message.chat.id]
    password = message.text

    await message.answer("Подключаюсь к личному кабинету...")

    try:
        users_chat_id[message.chat.id] = (login, await StudentAccount(login, password).driver)
    except IncorrectDataException:
        await message.answer("Неправильно введены данные, попробуйте ещё раз...", reply_markup=kb.LogInMenu)
        users_chat_id[message.chat.id] = None
    else:
        await message.answer("Подключение прошло успешно!", reply_markup=kb.StartMenu)


if __name__ == "__main__":
    dp.run_polling(bot)
