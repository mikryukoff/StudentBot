import traceback

import bot.exceptions.api_exceptions as api_exc
import bot.keyboards.menu_kb as kb
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message
from bot.database import users_data
from bot.lexicon import LEXICON, LEXICON_COMMANDS
from bot.utils import make_api_request
from environs import Env

from config import load_config

# Инициализация роутера и хранилища
router: Router = Router()
storage = MemoryStorage()

# Загрузка конфигурации приложения
config = load_config()

env = Env()
env.read_env()


# Определение состояний
class AuthStates(StatesGroup):
    waiting_for_login = State()
    waiting_for_password = State()


# Обработчик команды авторизации
@router.message(F.text == LEXICON_COMMANDS["authorisation"])
async def authorisation(message: Message, state: FSMContext):

    request_url = f"{env("API_URL")}/users/{message.chat.id}"

    try:
        await make_api_request(request_url, method="GET")

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

    except api_exc.UserNotFoundAPIException:
        # Устанавливаем состояние ожидания ввода логина
        await state.set_state(AuthStates.waiting_for_login)
        await message.answer(text=LEXICON["log_in"])

    except api_exc.APIException as e:
        await message.answer(text=LEXICON["error"])
        print(traceback.format_exc())


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

    # Получаем данные из состояния FSM
    user_data = await state.get_data()

    request_data = {
        "user_id": message.chat.id,
        "email": user_data.get("login"),
        "password": message.text
    }

    request_url = f"{env("API_URL")}/users/authorization"

    try:
        await message.answer(LEXICON["connecting_to_PA"])

        await make_api_request(request_url, method="POST", data=request_data)

        # Сохранение данных пользователя
        users_data[message.chat.id] = {
            "schedule_page": 0,              # Страница расписания
            "rating_page": 0                 # Страница рейтинга
        }

        # Очищаем состояние FSM
        await state.clear()

    except api_exc.ValidationAPIException:
        await message.answer(LEXICON["incorrect_user_data"])

    except api_exc.InvalidCredentialsAPIException:
        await message.answer(
            text=LEXICON["incorrect_user_data"],
            reply_markup=kb.LogInMenu
        )
        # Очищаем данные пользователя и состояние FSM
        users_data[message.chat.id] = {}
        await state.clear()

    except api_exc.APIException:
        await message.answer(text=LEXICON["error"])

    else:
        # Уведомление об успешном подключении
        await message.answer(
            text=LEXICON["successful_connection"],
            reply_markup=kb.StartMenu
        )
