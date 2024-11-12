from bot_config import BOT_TOKEN
from student_account import StudentAccount
from student_account.exceptions import IncorrectDataException

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
    await message.answer("✋ Привет,\n🤖 Меня зовут StudentBot.\n🦾 Я могу отправить расписание и баллы БРС!")
    await message.answer("⚠️ Для работы со мной, требуется авторизация по паролю и логину.", reply_markup=kb.LogInMenu)

    global users_chat_id
    users_chat_id.setdefault(message.chat.id, None)


@dp.message(F.text == "️🔙 В главное меню")
async def main_menu_button(message: Message):
    await message.answer("👣 Вы вернулись в главное меню!", reply_markup=kb.StartMenu)


############################## Расписание ##############################


@dp.message(F.text == "📅 Расписание")
async def schedule_menu(message: Message):
    await message.answer("🗓 Я могу отправить расписание на неделю или на конкретный день.", reply_markup=kb.ScheduleMenu)


@dp.message(F.text == "📆 Расписание на день")
async def send_day_schedule(message: Message):
    await message.answer("😊 Извините, данная функция в разработке, вы можете попросить расписание на неделю.")


@dp.message(F.text == "🗓 Расписание на неделю")
async def send_week_schedule(message: Message):
    global users_chat_id
    global schedule
    global week_days

    await message.answer("🧠 Обрабатываю запрос...")

    schedule = await users_chat_id[message.chat.id]["schedule"].week_schedule
    week_days = [i.split("\n\n")[0].strip(":") for i in schedule]
    page = users_chat_id[message.chat.id]["schedule_page"]

    if page != len(week_days) - 1 and page != 0:

        await message.answer(
            text=schedule[page],
            reply_markup=create_pagination_keyboard("backward_schedule", week_days[page], "forward_schedule")
            )

    elif page == 0:

        await message.answer(
            text=schedule[page], 
            reply_markup=create_pagination_keyboard(week_days[page], "forward_schedule")
            )
    else:

        await message.answer(
            text=schedule[page], 
            reply_markup=create_pagination_keyboard("backward_schedule", week_days[page])
            )


@dp.callback_query(F.data == "forward_schedule")
async def press_forward_schedule(callback: CallbackQuery):
    global users_chat_id
    global schedule
    global week_days

    page = users_chat_id[callback.from_user.id]["schedule_page"]

    if page + 1 < len(week_days) - 1:

        await callback.message.edit_text(
            text=schedule[page + 1],
            reply_markup=create_pagination_keyboard("backward_schedule", week_days[page + 1], "forward_schedule")
            )
    else:

        await callback.message.edit_text(
            text=schedule[page + 1],
            reply_markup=create_pagination_keyboard("backward_schedule", week_days[page + 1])
            )

    users_chat_id[callback.from_user.id]["schedule_page"] += 1

    await callback.answer()


@dp.callback_query(F.data == "backward_schedule")
async def press_backward_schedule(callback: CallbackQuery):
    global users_chat_id
    global schedule
    global week_days

    page = users_chat_id[callback.from_user.id]["schedule_page"]

    if page - 1 > 0:

        await callback.message.edit_text(
            text=schedule[page - 1],
            reply_markup=create_pagination_keyboard("backward_schedule", week_days[page - 1], "forward_schedule")
            )

    else:

        await callback.message.edit_text(
            text=schedule[page - 1],
            reply_markup=create_pagination_keyboard(week_days[page - 1], "forward_schedule")
            )

    users_chat_id[callback.from_user.id]["schedule_page"] -= 1

    await callback.answer()


############################## Баллы БРС ###############################


@dp.message(F.text == "📉 Баллы БРС")
async def rating_menu(message: Message):
    await message.answer("📝 Я могу отправить вам все ваши баллы БРС или только по конкретному предмету.", reply_markup=kb.RatingMenu)


@dp.message(F.text == "📝 Баллы по предмету")
async def send_discipline_rating(message: Message):
    await message.answer("😊 Извините, данная функция в разработке, зато две другие работают.")


@dp.message(F.text == "📕 Все баллы кратко")
async def send_short_rating(message: Message):
    global users_chat_id

    msg = await message.answer("🧠 Обрабатываю запрос...")

    rating = await users_chat_id[message.chat.id]["rating"].short_disciplines_rating

    await msg.edit_text(rating)


@dp.message(F.text == "📚 Все баллы подробно")
async def send_full_rating(message: Message):
    global users_chat_id
    global rating
    global disciplines

    await message.answer("🧠 Обрабатываю запрос...")

    rating = await users_chat_id[message.chat.id]["rating"].full_disciplines_rating
    # disciplines = [i.split(":\n")[0] for i in rating]
    disciplines = [str(i) for i in range(1, len(rating) + 1)]
    page = users_chat_id[message.chat.id]["rating_page"]

    if page != len(disciplines) - 1 and page != 0:

        await message.answer(
            text=rating[page],
            reply_markup=create_pagination_keyboard("backward_rating", disciplines[page], "forward_rating")
            )

    elif page == 0:

        await message.answer(
            text=rating[page], 
            reply_markup=create_pagination_keyboard(disciplines[page], "forward_rating")
            )
    else:

        await message.answer(
            text=rating[page], 
            reply_markup=create_pagination_keyboard("backward_rating", disciplines[page])
            )


@dp.callback_query(F.data == "forward_rating")
async def press_forward_rating(callback: CallbackQuery):
    global users_chat_id
    global rating
    global disciplines

    page = users_chat_id[callback.from_user.id]["rating_page"]

    if page + 1 < len(disciplines) - 1:

        await callback.message.edit_text(
            text=rating[page + 1],
            reply_markup=create_pagination_keyboard("backward_rating", disciplines[page + 1], "forward_rating")
            )
    else:

        await callback.message.edit_text(
            text=rating[page + 1],
            reply_markup=create_pagination_keyboard("backward_rating", disciplines[page + 1])
            )

    users_chat_id[callback.from_user.id]["rating_page"] += 1

    await callback.answer()


@dp.callback_query(F.data == "backward_rating")
async def press_backward_rating(callback: CallbackQuery):
    global users_chat_id
    global rating
    global disciplines

    page = users_chat_id[callback.from_user.id]["rating_page"]

    if page - 1 > 0:

        await callback.message.edit_text(
            text=rating[page - 1],
            reply_markup=create_pagination_keyboard("backward_rating", disciplines[page - 1], "forward_rating")
            )

    else:

        await callback.message.edit_text(
            text=rating[page - 1],
            reply_markup=create_pagination_keyboard(disciplines[page - 1], "forward_rating")
            )

    users_chat_id[callback.from_user.id]["rating_page"] -= 1

    await callback.answer()


@dp.message(F.text == "✅ Авторизация")
async def authorisation(message: Message):
    global users_chat_id

    if users_chat_id[message.chat.id]:
        await message.answer("❗️ Вы уже авторизованы!", reply_markup=kb.StartMenu)
        return

    await message.answer("▶️ Введите логин от личного кабинета: ")


@dp.message(F.text.contains("@"))
async def login(message: Message):
    global users_chat_id

    if users_chat_id[message.chat.id]:
        await message.answer("Попытка ввода логина...\nВы уже авторизованы!")
        return

    users_chat_id[message.chat.id] = message.text

    await message.answer("▶️ Введите пароль от личного кабинета: ")


# СДЕЛАТЬ НОРМАЛЬНУЮ ПРОВЕРКУ
@dp.message()
async def password(message: Message):
    global users_chat_id

    if not users_chat_id[message.chat.id] or "@" not in users_chat_id[message.chat.id]:
        await message.answer("❗️ Неверный логин! Повторите попытку: ")
        return

    if isinstance(users_chat_id[message.chat.id], dict):
        await message.answer("Попытка ввода пароля...\nВы уже авторизованы!")
        return

    login = users_chat_id[message.chat.id]
    password = message.text

    await message.answer("🛜 Подключаюсь к вашему личному кабинету...")

    try:
        account = await StudentAccount(login, password).driver

        users_chat_id[message.chat.id] = {
            "account": account,
            "schedule": account.schedule,
            "rating": account.rating,
            "schedule_page": 0,
            "rating_page": 0
        }

    except IncorrectDataException:
        await message.answer("❌ Неправильно введены данные, попробуйте ещё раз...", reply_markup=kb.LogInMenu)
        users_chat_id[message.chat.id] = None
    else:
        await message.answer("✅ Подключение прошло успешно!", reply_markup=kb.StartMenu)


if __name__ == "__main__":
    dp.run_polling(bot)
