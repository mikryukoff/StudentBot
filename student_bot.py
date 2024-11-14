from config_data.bot_config import load_config
from student_account import StudentAccount
from student_account.exceptions import IncorrectDataException

import keyboards.menu_kb as kb
from keyboards.pagination_kb import create_pagination_keyboard

from lexicon import LEXICON, LEXICON_COMMANDS

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery


config = load_config()

bot = Bot(token=config.tg_bot.token)
dp = Dispatcher()

users_chat_id: dict = {}


# Команда "/start"
@dp.message(CommandStart())
async def process_start_command(message: Message):
    await message.answer(LEXICON["/start"], reply_markup=kb.LogInMenu)

    global users_chat_id
    users_chat_id.setdefault(message.chat.id, None)


@dp.message(F.text == LEXICON_COMMANDS["to_main_menu"])
async def main_menu_button(message: Message):
    await message.answer(LEXICON["to_main_menu"], reply_markup=kb.StartMenu)


############################## Расписание ##############################


@dp.message(F.text == LEXICON_COMMANDS["schedule"])
async def schedule_menu(message: Message):
    await message.answer(LEXICON["schedule"], reply_markup=kb.ScheduleMenu)


@dp.message(F.text == LEXICON_COMMANDS["day_schedule"])
async def send_day_schedule(message: Message):
    await message.answer(LEXICON["unvailable"])


@dp.message(F.text == LEXICON_COMMANDS["week_schedule"])
async def send_week_schedule(message: Message):
    global users_chat_id
    global schedule
    global week_days

    await message.answer(LEXICON["processing"])

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


@dp.message(F.text == LEXICON_COMMANDS["rating"])
async def rating_menu(message: Message):
    await message.answer(LEXICON["rating"], reply_markup=kb.RatingMenu)


@dp.message(F.text == LEXICON_COMMANDS["discipline_rating"])
async def send_discipline_rating(message: Message):
    await message.answer(LEXICON["unvailable"])


@dp.message(F.text == LEXICON_COMMANDS["short_rating"])
async def send_short_rating(message: Message):
    global users_chat_id

    msg = await message.answer(LEXICON["processing"])

    rating = await users_chat_id[message.chat.id]["rating"].short_disciplines_rating

    await msg.edit_text(rating)


@dp.message(F.text == LEXICON_COMMANDS["full_rating"])
async def send_full_rating(message: Message):
    global users_chat_id
    global rating
    global disciplines

    await message.answer(LEXICON["processing"])

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


@dp.message(F.text == LEXICON_COMMANDS["authorisation"])
async def authorisation(message: Message):
    global users_chat_id

    if users_chat_id[message.chat.id]:
        await message.answer(LEXICON["already_auth"], reply_markup=kb.StartMenu)
        return

    await message.answer(LEXICON["log_in"])


@dp.message(F.text.contains("@"))
async def login(message: Message):
    global users_chat_id

    if users_chat_id[message.chat.id]:
        await message.answer(LEXICON["already_auth"])
        return

    users_chat_id[message.chat.id] = message.text

    await message.answer(LEXICON["pass_in"])


# СДЕЛАТЬ НОРМАЛЬНУЮ ПРОВЕРКУ
@dp.message()
async def password(message: Message):
    global users_chat_id

    if not users_chat_id[message.chat.id] or "@" not in users_chat_id[message.chat.id]:
        await message.answer(LEXICON["incorrect_user_data"])
        return

    if isinstance(users_chat_id[message.chat.id], dict):
        await message.answer(LEXICON["already_auth"])
        return

    login = users_chat_id[message.chat.id]
    password = message.text

    await message.answer(LEXICON["connecting_to_PA"])

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
        await message.answer(LEXICON["incorrect_user_data"], reply_markup=kb.LogInMenu)
        users_chat_id[message.chat.id] = None
    else:
        await message.answer(LEXICON["successful_connection"], reply_markup=kb.StartMenu)


if __name__ == "__main__":
    dp.run_polling(bot)
