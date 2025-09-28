from datetime import datetime, timedelta

import bot.exceptions.api_exceptions as api_exc
import bot.keyboards.menu_kb as kb
from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from bot.database import users_data
from bot.filters import DateFilter
from bot.keyboards.menu_kb import week_dates_keyboard
from bot.keyboards.pagination_kb import create_pagination_keyboard
from bot.lexicon import LEXICON, LEXICON_COMMANDS
from bot.utils import make_api_request, make_schedule_request
from environs import Env

from config import load_config

# Создание экземпляра Router
router: Router = Router()

# Загрузка конфигурации
config = load_config()

# Глобальные переменные для расписания
schedule: list = []
week_days: list = []

env = Env()
env.read_env()


# Хендлер для команды "Расписание"
@router.message(F.text == LEXICON_COMMANDS["schedule"])
async def schedule_menu(message: Message):
    global week_days

    request_url = f"{env("API_URL")}/users/{message.chat.id}"

    if not week_days:
        try:
            # Извлечение дней недели из расписания
            user_data = await make_api_request(request_url)
        except api_exc.UserNotFoundAPIException:
            await message.answer(text="Авторизуйся", reply_markup=kb.LogInMenu)
            return
        except api_exc.APIException:
            await message.answer(text=LEXICON["error"])
            return

        # Преобразуем строку в date, если необходимо
        if isinstance(user_data["week_start_date"], str):
            start_date = datetime.strptime(user_data["week_start_date"], "%Y-%m-%d").date()
        else:
            start_date = user_data["week_start_date"]

        RUS_WEEKDAYS = {0: "Пн", 1: "Вт", 2: "Ср", 3: "Чт", 4: "Пт", 5: "Сб", 6: "Вс"}
        week_days = [
            f"{RUS_WEEKDAYS[(start_date + timedelta(days=i)).weekday()]}. - {(start_date + timedelta(days=i)).strftime('%d.%m')}" 
            for i in range(7)
        ]

    # Отправляем пользователю меню с кнопками для работы с расписанием
    await message.answer(
        text=LEXICON["schedule"],
        reply_markup=kb.ScheduleMenu
    )


# Хендлер для отображения меню расписания на день
@router.message(F.text == LEXICON_COMMANDS["day_schedule"])
async def day_schedule_menu(message: Message):
    global week_days

    msg = await message.answer(LEXICON["processing"])

    # Удаление промежуточного сообщения
    await message.bot.delete_message(
        chat_id=msg.chat.id,
        message_id=msg.message_id
    )

    # Отправка клавиатуры с выбором дня
    await message.answer(
        text=LEXICON["day_schedule"],
        reply_markup=week_dates_keyboard(week_days)
    )


# Хендлер для отображения расписания на определённый день
@router.message(DateFilter())
async def send_day_schedule(message: Message):
    msg = await message.answer(LEXICON["processing"])

    status, data = await make_schedule_request(
        user_id=message.chat.id,
        method="GET",
        params={"day": week_days.index(message.text)}
    )

    if not status:
        await message.answer(**data)
        return

    text = f"📌{message.text}:\n\n"
    for discipline, time, location in data:
        # Если есть URL, оформляем их как ссылки в формате Markdown
        if "https://" in str(location) or "http://" in str(location):
            location = f"[{location}]({location})"
        text += f"`{time}`:\n*{discipline}*\n{location}\n\n"

    # Редактирование сообщения с расписанием
    await msg.edit_text(text=text, parse_mode="Markdown")


# Хендлер для отображения расписания на неделю с пагинацией
@router.message(F.text == LEXICON_COMMANDS["week_schedule"])
async def send_week_schedule(message: Message):
    global schedule
    global week_days

    await message.answer(LEXICON["processing"])

    for day in week_days:
        text = f"📌{day}:\n\n"

        status, data = await make_schedule_request(
            user_id=message.chat.id,
            method="GET",
            params={"day": week_days.index(day)}
        )

        if not status:
            await message.answer(**data)
            return

        for discipline, time, location in data:
            # Если есть URL, оформляем их как ссылки в формате Markdown
            if "https://" in str(location) or "http://" in str(location):
                location = f"[{location}]({location})"
            text += f"`{time}`:\n*{discipline}*\n{location}\n\n"

        schedule.append(text)

    # Текущая страница
    page = users_data[message.chat.id]["schedule_page"]

    # Пагинация в зависимости от текущей страницы
    if page != len(week_days) - 1 and page != 0:
        await message.answer(
            text=schedule[page],
            parse_mode="Markdown",
            reply_markup=create_pagination_keyboard(
                "backward_schedule", week_days[page], "forward_schedule"
            )
        )
    elif page == 0:
        await message.answer(
            text=schedule[page],
            parse_mode="Markdown",
            reply_markup=create_pagination_keyboard(
                week_days[page], "forward_schedule"
            )
        )
    else:
        await message.answer(
            text=schedule[page],
            parse_mode="Markdown",
            reply_markup=create_pagination_keyboard(
                "backward_schedule", week_days[page]
            )
        )


# Хендлер для кнопки ">>" в пагинации расписания
@router.callback_query(F.data == "forward_schedule")
async def press_forward_schedule(callback: CallbackQuery):
    global schedule
    global week_days

    # Текущая страница
    page = users_data[callback.from_user.id]["schedule_page"]

    # Пагинация в зависимости от текущей страницы
    if page + 1 < len(week_days) - 1:
        await callback.message.edit_text(
            text=schedule[page + 1],
            parse_mode="Markdown",
            reply_markup=create_pagination_keyboard(
                "backward_schedule", week_days[page + 1], "forward_schedule"
            )
        )
    else:
        await callback.message.edit_text(
            text=schedule[page + 1],
            parse_mode="Markdown",
            reply_markup=create_pagination_keyboard(
                "backward_schedule", week_days[page + 1]
            )
        )

    # Сохраняем в базу, что пользователь перешёл на следующую страницу
    users_data[callback.from_user.id]["schedule_page"] += 1

    await callback.answer()


# Хендлер для кнопки "<<" в пагинации расписания
@router.callback_query(F.data == "backward_schedule")
async def press_backward_schedule(callback: CallbackQuery):
    global schedule
    global week_days

    # Текущая страница
    page = users_data[callback.from_user.id]["schedule_page"]

    # Пагинация в зависимости от текущей страницы
    if page - 1 > 0:
        await callback.message.edit_text(
            text=schedule[page - 1],
            parse_mode="Markdown",
            reply_markup=create_pagination_keyboard(
                "backward_schedule", week_days[page - 1], "forward_schedule"
            )
        )
    else:
        await callback.message.edit_text(
            text=schedule[page - 1],
            parse_mode="Markdown",
            reply_markup=create_pagination_keyboard(
                week_days[page - 1], "forward_schedule"
            )
        )

    # Сохраняем в базу, что пользователь перешёл на предыдущую страницу
    users_data[callback.from_user.id]["schedule_page"] -= 1

    await callback.answer()


# Хендлер для обновления расписания
@router.message(F.text == LEXICON_COMMANDS["update_schedule"])
async def update_student_rating(message: Message):
    msg = await message.answer(text=LEXICON["processing"])

    status, data = await make_schedule_request(message.chat.id, method="PUT")

    if not status:
        await message.answer(**data)
        return

    # Обновляем данные пользователя
    users_data[message.chat.id] = {
        "schedule_page": 0,              # Страница расписания
        "rating_page": 0                 # Страница рейтинга
    }

    await msg.edit_text(text=LEXICON["successful_updating"])
