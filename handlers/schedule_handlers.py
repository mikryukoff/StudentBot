import keyboards.menu_kb as kb
from keyboards.pagination_kb import create_pagination_keyboard

from filters import DateFilter

from database import users_data

from lexicon import LEXICON, LEXICON_COMMANDS

from aiogram import F, Router
from aiogram.types import Message, CallbackQuery


router: Router = Router()
schedule: list = []
week_days: list = []


@router.message(F.text == LEXICON_COMMANDS["schedule"])
async def schedule_menu(message: Message):
    await message.answer(
        text=LEXICON["schedule"],
        reply_markup=kb.ScheduleMenu
        )


@router.message(F.text == LEXICON_COMMANDS["day_schedule"])
async def day_schedule_menu(message: Message):

    schedule = users_data[message.chat.id]["schedule"]
    schedule = await schedule.week_schedule

    week_days = [i.split("\n\n")[0].strip(":") for i in schedule]

    await message.answer(
        LEXICON["day_schedule"],
        reply_markup=kb.week_dates_keyboard(week_days)
        )


@router.message(DateFilter())
async def send_day_schedule(message: Message):
    msg = await message.answer(LEXICON["processing"])

    day_schedule = users_data[message.chat.id]["schedule"]
    day_schedule = await day_schedule.day_schedule(date=message.text)

    await msg.edit_text(text=day_schedule)


@router.message(F.text == LEXICON_COMMANDS["week_schedule"])
async def send_week_schedule(message: Message):
    global schedule
    global week_days

    await message.answer(LEXICON["processing"])

    schedule = users_data[message.chat.id]["schedule"]
    schedule = await schedule.week_schedule

    week_days = [i.split("\n\n")[0].strip(":") for i in schedule]
    page = users_data[message.chat.id]["schedule_page"]

    if page != len(week_days) - 1 and page != 0:

        await message.answer(
            text=schedule[page],
            reply_markup=create_pagination_keyboard(
                "backward_schedule", week_days[page], "forward_schedule"
                )
            )

    elif page == 0:

        await message.answer(
            text=schedule[page],
            reply_markup=create_pagination_keyboard(
                week_days[page], "forward_schedule"
                )
            )
    else:

        await message.answer(
            text=schedule[page],
            reply_markup=create_pagination_keyboard(
                "backward_schedule", week_days[page]
                )
            )


@router.callback_query(F.data == "forward_schedule")
async def press_forward_schedule(callback: CallbackQuery):
    global schedule
    global week_days

    page = users_data[callback.from_user.id]["schedule_page"]

    if page + 1 < len(week_days) - 1:

        await callback.message.edit_text(
            text=schedule[page + 1],
            reply_markup=create_pagination_keyboard(
                "backward_schedule", week_days[page + 1], "forward_schedule"
                )
            )
    else:

        await callback.message.edit_text(
            text=schedule[page + 1],
            reply_markup=create_pagination_keyboard(
                "backward_schedule", week_days[page + 1]
                )
            )

    users_data[callback.from_user.id]["schedule_page"] += 1

    await callback.answer()


@router.callback_query(F.data == "backward_schedule")
async def press_backward_schedule(callback: CallbackQuery):
    global schedule
    global week_days

    page = users_data[callback.from_user.id]["schedule_page"]

    if page - 1 > 0:

        await callback.message.edit_text(
            text=schedule[page - 1],
            reply_markup=create_pagination_keyboard(
                "backward_schedule", week_days[page - 1], "forward_schedule"
                )
            )

    else:

        await callback.message.edit_text(
            text=schedule[page - 1],
            reply_markup=create_pagination_keyboard(
                week_days[page - 1], "forward_schedule"
                )
            )

    users_data[callback.from_user.id]["schedule_page"] -= 1

    await callback.answer()
