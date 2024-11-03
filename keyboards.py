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
            KeyboardButton(text="Баллы БРС")
        ]
    ],
    resize_keyboard=True,
    one_time_keyboard=False,
    input_field_placeholder="Начальное меню"
)