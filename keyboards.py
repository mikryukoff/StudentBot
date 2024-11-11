from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, KeyboardButton, InlineKeyboardButton


LogInMenu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="✅ Авторизация"),
        ]
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
    input_field_placeholder="Меню авторизации"
)

StartMenu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="📅 Расписание"),
            KeyboardButton(text="📉 Баллы БРС")
        ]
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
    input_field_placeholder="Начальное меню"
)

RatingMenu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Выбрать предмет"),
            KeyboardButton(text="Баллы кратко"),
            KeyboardButton(text="Баллы подробно"),
            KeyboardButton(text="Главное меню")
        ]
    ],
    resize_keyboard=True,
    one_time_keyboard=False,
    input_field_placeholder="БРС меню"
)

ScheduleMenu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="На неделю"),
            KeyboardButton(text="На день"),
            KeyboardButton(text="Главное меню")
        ]
    ],
    resize_keyboard=True,
    one_time_keyboard=False,
    input_field_placeholder="БРС меню"
)