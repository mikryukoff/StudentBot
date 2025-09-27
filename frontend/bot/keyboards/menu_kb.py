# Импорты необходимых библиотек
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from bot.lexicon import LEXICON_COMMANDS


# Меню авторизации
LogInMenu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text=LEXICON_COMMANDS["authorisation"]),    # Кнопка авторизации
        ]
    ],
    resize_keyboard=True,                         # Автоматическая настройка размера клавиатуры
    one_time_keyboard=True,                       # Клавиатура будет скрыта после использования
    input_field_placeholder="Меню авторизации"    # Подсказка для поля ввода
)

# Начальное меню
StartMenu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text=LEXICON_COMMANDS["schedule"]),    # Кнопка "Расписание"
            KeyboardButton(text=LEXICON_COMMANDS["rating"])       # Кнопка "Баллы БРС"
        ]
    ],
    resize_keyboard=True,                       # Автоматическая настройка размера клавиатуры
    one_time_keyboard=True,                     # Клавиатура будет скрыта после использования
    input_field_placeholder="Начальное меню"    # Подсказка для поля ввода
)

# Меню с рейтингами
RatingMenu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text=LEXICON_COMMANDS["discipline_rating"]),    # Кнопка "Баллы по предмету"
            KeyboardButton(text=LEXICON_COMMANDS["short_rating"]),         # Кнопка "Все баллы кратко"
            KeyboardButton(text=LEXICON_COMMANDS["full_rating"])           # Кнопка "Все баллы подробно"
        ],
        [
            KeyboardButton(text=LEXICON_COMMANDS["to_main_menu"]),         # Кнопка "В главное меню"
            KeyboardButton(text=LEXICON_COMMANDS["update_rating"])         # Кнопка "Обновить баллы"
        ]
    ],
    resize_keyboard=True,                 # Автоматическая настройка размера клавиатуры
    one_time_keyboard=False,              # Клавиатура не скрывается после использования
    input_field_placeholder="БРС меню"    # Подсказка для поля ввода
)

# Меню с расписанием
ScheduleMenu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text=LEXICON_COMMANDS["week_schedule"]),      # Кнопка "Расписание на неделю"
            KeyboardButton(text=LEXICON_COMMANDS["day_schedule"])        # Кнопка "Расписание на день"
        ],
        [
            KeyboardButton(text=LEXICON_COMMANDS["to_main_menu"]),       # Кнопка "В главное меню"
            KeyboardButton(text=LEXICON_COMMANDS["update_schedule"]),    # Кнопка "Обновить расписание"
        ]
    ],
    resize_keyboard=True,                        # Автоматическая настройка размера клавиатуры
    one_time_keyboard=False,                     # Клавиатура не скрывается после использования
    input_field_placeholder="Меню расписания"    # Подсказка для поля ввода
)


# Функция для генерации клавиатуры с датами недели
def week_dates_keyboard(dates: list) -> ReplyKeyboardMarkup:
    keyboard = [[KeyboardButton(text=i) for i in dates]]                        # Создание кнопок для каждой даты
    keyboard.append([KeyboardButton(text=LEXICON_COMMANDS["to_main_menu"])])    # Кнопка "В главное меню"

    return ReplyKeyboardMarkup(
        keyboard=keyboard,                       # Клавиатура с кнопками
        resize_keyboard=True,                    # Автоматическая настройка размера клавиатуры
        one_time_keyboard=False,                 # Клавиатура не скрывается после использования
        input_field_placeholder="Даты недели"    # Подсказка для поля ввода
    )


# Функция для генерации клавиатуры с предметами рейтинга
def discipline_rating(disciplines: list) -> ReplyKeyboardMarkup:
    keyboard = [[KeyboardButton(text=i)] for i in disciplines]                  # Создание кнопок для каждого предмета
    keyboard.append([KeyboardButton(text=LEXICON_COMMANDS["to_main_menu"])])    # Кнопка "В главное меню"

    return ReplyKeyboardMarkup(
        keyboard=keyboard,                    # Клавиатура с кнопками
        resize_keyboard=True,                 # Автоматическая настройка размера клавиатуры
        one_time_keyboard=False,              # Клавиатура не скрывается после использования
        input_field_placeholder="Предметы"    # Подсказка для поля ввода
    )
