from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from lexicon import LEXICON, LEXICON_COMMANDS


LogInMenu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text=LEXICON_COMMANDS["authorisation"]),
        ]
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
    input_field_placeholder="Меню авторизации"
)

StartMenu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text=LEXICON_COMMANDS["schedule"]),
            KeyboardButton(text=LEXICON_COMMANDS["rating"])
        ]
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
    input_field_placeholder="Начальное меню"
)

RatingMenu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text=LEXICON_COMMANDS["discipline_rating"]),
            KeyboardButton(text=LEXICON_COMMANDS["short_rating"]),
            KeyboardButton(text=LEXICON_COMMANDS["full_rating"])
        ],
        [
            KeyboardButton(text=LEXICON_COMMANDS["to_main_menu"]),
            KeyboardButton(text=LEXICON_COMMANDS["update_rating"])
        ]
    ],
    resize_keyboard=True,
    one_time_keyboard=False,
    input_field_placeholder="БРС меню"
)

ScheduleMenu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text=LEXICON_COMMANDS["week_schedule"]),
            KeyboardButton(text=LEXICON_COMMANDS["day_schedule"])
        ],
        [
            KeyboardButton(text=LEXICON_COMMANDS["to_main_menu"]),
            KeyboardButton(text=LEXICON_COMMANDS["update_schedule"]),
        ]
    ],
    resize_keyboard=True,
    one_time_keyboard=False,
    input_field_placeholder="Меню расписания"
)


def week_dates_keyboard(dates: list) -> ReplyKeyboardMarkup:
    keyboard = [[KeyboardButton(text=i) for i in dates]]
    keyboard.append([KeyboardButton(text=LEXICON_COMMANDS["to_main_menu"])])

    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        one_time_keyboard=False,
        input_field_placeholder="Даты недели"
        )


def discipline_rating(disciplines: list) -> ReplyKeyboardMarkup:
    keyboard = [[KeyboardButton(text=i)] for i in disciplines]
    keyboard.append([KeyboardButton(text=LEXICON_COMMANDS["to_main_menu"])])

    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        one_time_keyboard=False,
        input_field_placeholder="Предметы"
        )
