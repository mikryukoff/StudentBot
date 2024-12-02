# Импорты библиотек Aiogram
from aiogram import F, Router
from aiogram.types import Message, CallbackQuery

from datetime import datetime, timedelta
import locale

# Импорты пользовательских модулей
from keyboards.menu_kb import ScheduleMenu, week_dates_keyboard
from keyboards.pagination_kb import create_pagination_keyboard

from config_data.config import load_config

from cipher import PassCipher

# Импорт инициализатора таблиц БД, словарь для хранения страниц и типы
from database import initialize_databases, users_data
from database import WeeklySchedule, Grades, Users

from filters import DateFilter

from student_account import StudentAccount

from lexicon import LEXICON, LEXICON_COMMANDS


locale.setlocale(locale.LC_TIME, "ru_RU.UTF-8")

# Создание экземпляра Router
router: Router = Router()

# Загрузка конфигурации
config = load_config()

# Создание объекта шифрования для паролей
cipher: PassCipher = PassCipher(config.user_data.secret_key)

# Глобальные переменные для расписания
schedule: list = []
week_days: list = []

# Инициализируем кортеж с таблицами
tables: tuple[Users, Grades, WeeklySchedule] = ()


# Хендлер для команды "Расписание"
@router.message(F.text == LEXICON_COMMANDS["schedule"])
async def schedule_menu(message: Message):
    global tables

    tables = await initialize_databases()

    # Отправляем пользователю меню с кнопками для работы с расписанием
    await message.answer(
        text=LEXICON["schedule"],
        reply_markup=ScheduleMenu
    )


# Хендлер для отображения меню расписания на день
@router.message(F.text == LEXICON_COMMANDS["day_schedule"])
async def day_schedule_menu(message: Message):
    global tables
    global week_days

    msg = await message.answer(LEXICON["processing"])

    if not week_days:
        users_table = tables[0]

        # Извлечение дней недели из расписания
        user_data = await users_table.select_user_data(chat_id=message.chat.id)
        week_start = datetime.strptime(user_data[2], "%Y-%m-%d")
        week_days = [(week_start + timedelta(days=i)).strftime("%a - %d.%m")
                     for i in range(7)]

    # Удаление промежуточного сообщения
    await message.bot.delete_message(
        chat_id=msg.chat.id,
        message_id=msg.message_id
    )

    # Отправка клавиатуры с выбором дня
    await message.answer(
        LEXICON["day_schedule"],
        reply_markup=week_dates_keyboard(week_days)
    )


# Хендлер для отображения расписания на определённый день
@router.message(DateFilter())
async def send_day_schedule(message: Message):
    global tables

    schedule_table = tables[2]

    msg = await message.answer(LEXICON["processing"])

    _, rows = await schedule_table.select_discipline(
        chat_id=message.chat.id,
        day_of_week=week_days.index(message.text)
    )

    text = f"{message.text}:\n\n"
    for discipline, time, location in rows:
        text += f"{time}:\n{discipline}\n{location}\n\n"

    # Редактирование сообщения с расписанием
    await msg.edit_text(text=text)


# Хендлер для отображения расписания на неделю с пагинацией
@router.message(F.text == LEXICON_COMMANDS["week_schedule"])
async def send_week_schedule(message: Message):
    global schedule
    global week_days
    global tables

    if not week_days:
        users_table = tables[0]

        # Извлечение дней недели из расписания
        user_data = await users_table.select_user_data(chat_id=message.chat.id)
        week_days = [(user_data[2] + timedelta(days=i)).strftime("%a. - %d.%m")
                     for i in range(7)]

    schedule_table = tables[2]

    await message.answer(LEXICON["processing"])

    for day in week_days:
        text = f"{day}:\n\n"

        _, rows = await schedule_table.select_discipline(
            chat_id=message.chat.id,
            day_of_week=week_days.index(day)
        )

        for discipline, time, location in rows:
            text += f"{time}:\n{discipline}\n{location}\n\n"

        schedule.append(text)

    # Текущая страница
    page = users_data[message.chat.id]["schedule_page"]

    # Пагинация в зависимости от текущей страницы
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

    # Сохраняем в базу, что пользователь перешёл на предыдущую страницу
    users_data[callback.from_user.id]["schedule_page"] -= 1

    await callback.answer()


# Хендлер для обновления расписания
@router.message(F.text == LEXICON_COMMANDS["update_schedule"])
async def update_student_rating(message: Message):
    global tables

    users_table = tables[0]

    msg = await message.answer(text=LEXICON["processing"])

    # Записываем логин и пароль пользователя
    # Пароль дешифруем для авторизации
    login, password, _ = await users_table.select_user_data(chat_id=message.chat.id)
    password = cipher.decrypt_password(password)

    # Обновляем сессию
    account = await StudentAccount(
        user_login=login,
        user_pass=password,
        chat_id=message.chat.id
    ).driver

    # Обновляем данные пользователя
    users_data[message.chat.id] = {
        "schedule_page": 0,              # Страница расписания
        "rating_page": 0                 # Страница рейтинга
    }

    await account.schedule.week_schedule(key="update")

    await msg.edit_text(text=LEXICON["successful_updating"])
