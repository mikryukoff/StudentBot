# Импорты модулей и библиотек
from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from datetime import datetime, timedelta

# Импорты пользовательских модулей
from config_data.config import load_config

from cipher import PassCipher

# Импорт инициализатора таблиц БД, словарь для хранения страниц и типы
from database import initialize_databases, users_data
from database import WeeklySchedule, Grades, Users

from lexicon import LEXICON, LEXICON_COMMANDS

from student_account import StudentAccount
from student_account.exceptions import IncorrectDataException

import keyboards.menu_kb as kb

# Инициализация роутера и хранилища
router: Router = Router()
storage = MemoryStorage()

# Загрузка конфигурации приложения
config = load_config()

# Инициализация шифра для работы с паролями
cipher: PassCipher = PassCipher(config.user_data.secret_key)

# Инициализируем кортеж с таблицами
tables: tuple[Users, Grades, WeeklySchedule] = ()


# Определение состояний
class AuthStates(StatesGroup):
    waiting_for_login = State()
    waiting_for_password = State()


# Обработчик команды авторизации
@router.message(F.text == LEXICON_COMMANDS["authorisation"])
async def authorisation(message: Message, state: FSMContext):
    global tables

    tables = await initialize_databases()
    users_table = tables[0]

    # Если пользователь уже авторизован
    if await users_table.is_user_in_db(message.chat.id):
        await message.answer(
            text=LEXICON["already_auth"],
            reply_markup=kb.StartMenu
        )

        # Сохранение данных пользователя
        users_data[message.chat.id] = {
            "schedule_page": 0,              # Страница расписания
            "rating_page": 0                 # Страница рейтинга
        }
        return

    # Устанавливаем состояние ожидания ввода логина
    await state.set_state(AuthStates.waiting_for_login)
    await message.answer(text=LEXICON["log_in"])


# Обработчик ввода логина
@router.message(AuthStates.waiting_for_login, F.text.contains("@"))
async def login(message: Message, state: FSMContext):
    # Сохраняем логин в данные FSM
    await state.update_data(login=message.text)

    # Устанавливаем состояние ожидания ввода пароля
    await state.set_state(AuthStates.waiting_for_password)
    await message.answer(text=LEXICON["pass_in"])


# Обработчик ввода пароля
@router.message(AuthStates.waiting_for_password)
async def password(message: Message, state: FSMContext):
    global tables

    users_table = tables[0]

    # Получаем данные из состояния FSM
    user_data = await state.get_data()
    login = user_data.get("login")
    password = message.text

    # Проверка корректности логина
    if not login or "@" not in login:
        await message.answer(LEXICON["incorrect_user_data"])
        await state.clear()
        return

    # Уведомление о подключении
    await message.answer(LEXICON["connecting_to_PA"])

    try:
        # Подключение к аккаунту студента
        account = await StudentAccount(
            user_login=login,
            user_pass=password,
            chat_id=message.chat.id
        ).driver

        # Сохранение данных пользователя
        users_data[message.chat.id] = {
            "schedule_page": 0,              # Страница расписания
            "rating_page": 0                 # Страница рейтинга
        }

        # Очищаем состояние FSM
        await state.clear()

    except IncorrectDataException:
        # Если данные неверны, отправляем сообщение об ошибке
        await message.answer(
            text=LEXICON["incorrect_user_data"],
            reply_markup=kb.LogInMenu
        )

        # Очищаем данные пользователя и состояние FSM
        users_data[message.chat.id] = {}
        await state.clear()

    else:
        # Получаем текущую дату
        today = datetime.today()

        # Находим начало недели (понедельник)
        week_start = today - timedelta(days=today.weekday())

        # Если пользователь успешно авторизовался, добавляем его в БД
        await users_table.add_user_in_table(
            chat_id=message.chat.id,
            login=login,
            password_hash=cipher.encrypt_password(password),
            current_week_start=week_start.strftime('%Y-%m-%d')
        )

        # Записываем все данные пользователя в БД
        await account.schedule.week_schedule(key="insert")
        await account.rating.full_disciplines_rating(key="insert")

        # Уведомление об успешном подключении
        await message.answer(
            text=LEXICON["successful_connection"],
            reply_markup=kb.StartMenu
        )
