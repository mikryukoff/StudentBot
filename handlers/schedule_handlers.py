# Импорты библиотек Aiogram
from aiogram import F, Router
from aiogram.types import Message, CallbackQuery

# Импорты пользовательских модулей
from keyboards.menu_kb import ScheduleMenu, week_dates_keyboard
from keyboards.pagination_kb import create_pagination_keyboard

from config_data.config import load_config

from cipher import PassCipher

from database import users_data

from filters import DateFilter

from student_account import StudentAccount

from lexicon import LEXICON, LEXICON_COMMANDS


# Создание экземпляра Router
router: Router = Router()

# Загрузка конфигурации
config = load_config()

# Создание объекта шифрования для паролей
cipher: PassCipher = PassCipher(config.user_data.secret_key)

# Глобальные переменные для расписания
schedule: list = []
week_days: list = []


# Хендлер для команды "Расписание"
@router.message(F.text == LEXICON_COMMANDS["schedule"])
async def schedule_menu(message: Message):
    # Отправляем пользователю меню с кнопками для работы с расписанием
    await message.answer(
        text=LEXICON["schedule"],
        reply_markup=ScheduleMenu
    )


# Хендлер для отображения меню расписания на день
@router.message(F.text == LEXICON_COMMANDS["day_schedule"])
async def day_schedule_menu(message: Message):
    msg = await message.answer(LEXICON["processing"])

    # Сохраняем в переменную объект ScheduleParser
    # и вызываем метод для загрузки расписания на неделю
    schedule = users_data[message.chat.id]["data"]["schedule"]
    schedule = await schedule.week_schedule

    # Извлечение дней недели из расписания
    week_days = [i.split("\n\n")[0].strip(":") for i in schedule]

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
    msg = await message.answer(LEXICON["processing"])

    # Сохраняем в переменную объект ScheduleParser
    # и вызываем метод для загрузки расписания на выбранный день
    day_schedule = users_data[message.chat.id]["data"]["schedule"]
    day_schedule = await day_schedule.day_schedule(date=message.text)

    # Редактирование сообщения с расписанием
    await msg.edit_text(text=day_schedule)


# Хендлер для отображения расписания на неделю с пагинацией
@router.message(F.text == LEXICON_COMMANDS["week_schedule"])
async def send_week_schedule(message: Message):
    global schedule
    global week_days

    await message.answer(LEXICON["processing"])

    # Сохраняем в переменную объект ScheduleParser
    # и вызываем метод для загрузки расписания на неделю
    schedule = users_data[message.chat.id]["data"]["schedule"]
    schedule = await schedule.week_schedule

    # Извлечение дней недели из расписания
    week_days = [i.split("\n\n")[0].strip(":") for i in schedule]

    # Текущая страница
    page = users_data[message.chat.id]["data"]["schedule_page"]

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
    page = users_data[callback.from_user.id]["data"]["schedule_page"]

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
    users_data[callback.from_user.id]["data"]["schedule_page"] += 1

    await callback.answer()


# Хендлер для кнопки "<<" в пагинации расписания
@router.callback_query(F.data == "backward_schedule")
async def press_backward_schedule(callback: CallbackQuery):
    global schedule
    global week_days

    # Текущая страница
    page = users_data[callback.from_user.id]["data"]["schedule_page"]

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
    users_data[callback.from_user.id]["data"]["schedule_page"] -= 1

    await callback.answer()


# Хендлер для обновления расписания
@router.message(F.text == LEXICON_COMMANDS["update_schedule"])
async def update_student_rating(message: Message):
    msg = await message.answer(text=LEXICON["processing"])

    # Записываем логин и пароль пользователя
    # Пароль дешифруем для авторизации
    login = users_data[message.chat.id]["login"]
    password = cipher.decrypt_password(users_data[message.chat.id]["password"])

    # Обновляем сессию
    account = await StudentAccount(
        user_login=login,
        user_pass=password
    ).driver

    # Обновляем данные пользователя
    users_data[message.chat.id]["data"] = {
        "account": account,              # Данные аккаунта
        "schedule": account.schedule,    # Объект для работы с расписанием
        "rating": account.rating,        # Объект для работы с баллами
        "schedule_page": 0,              # Страница расписания
        "rating_page": 0                 # Страница рейтинга
    }

    # Обновляем информацию по баллам в базе
    users_data[message.chat.id]["data"]["account"].update_student_data(key="schedule")

    await msg.edit_text(text=LEXICON["successful_updating"])
