from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


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
            KeyboardButton(text="📝 Баллы по предмету"), 
            KeyboardButton(text="📕 Все баллы кратко"), 
            KeyboardButton(text="📚 Все баллы подробно")
        ],
        [
            KeyboardButton(text="️🔙 В главное меню")
        ]
    ],
    resize_keyboard=True,
    one_time_keyboard=False,
    input_field_placeholder="БРС меню"
)

ScheduleMenu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="🗓 Расписание на неделю"), 
            KeyboardButton(text="📆 Расписание на день")
        ],
        [
            KeyboardButton(text="️🔙 В главное меню")
        ]
    ],
    resize_keyboard=True,
    one_time_keyboard=False,
    input_field_placeholder="Меню расписания"
)


def week_dates_keyboard(dates: list) -> ReplyKeyboardMarkup:
    keyboard = list()
    buttons = list()

    for day in dates:
        buttons.append(KeyboardButton(text=day))

    keyboard.append(buttons)
    keyboard.append([KeyboardButton(text="️🔙 В главное меню")])

    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        one_time_keyboard=False,
        input_field_placeholder="Даты недели"
        )
