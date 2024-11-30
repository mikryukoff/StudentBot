# Импорты пользовательских модулей
import keyboards.menu_kb as kb
from keyboards.pagination_kb import create_pagination_keyboard

from config_data.config import load_config

from cipher import PassCipher

from database import users_data

from filters import DisciplineFilter

from student_account import StudentAccount

from lexicon import LEXICON, LEXICON_COMMANDS

# Импорты библиотек Aiogram
from aiogram import F, Router
from aiogram.types import Message, CallbackQuery

# Инициализация роутера
router: Router = Router()

# Загрузка конфигурации и инициализация шифровщика
config = load_config()
cipher: PassCipher = PassCipher(config.user_data.secret_key)

# Глобальные переменные для дисциплин, страниц и рейтинга
disciplines: list = []    # Список дисциплин
pages: list = []          # Список страниц
rating_list: list = []    # Список рейтингов


# Меню баллов БРС
@router.message(F.text == LEXICON_COMMANDS["rating"])
async def rating_menu(message: Message):
    # Отправляем пользователю меню с кнопками для работы с баллами
    await message.answer(
        text=LEXICON["rating"],
        reply_markup=kb.RatingMenu
    )


# Меню баллов по дисциплинам
@router.message(F.text == LEXICON_COMMANDS["discipline_rating"])
async def discipline_rating_menu(message: Message):
    global disciplines

    await message.answer(text=LEXICON["processing"])

    # Сохраняем в переменную объект RatingParser
    # и вызываем метод для загрузки баллов по всем предметам
    rating = users_data[message.chat.id]["data"]["rating"]
    rating = await rating.full_disciplines_rating

    # Формируем список дисциплин
    if not disciplines:
        disciplines.extend([f"📌{i.split(':')[0]}" for i in rating])

    # Отправляем пользователю меню с выбором предметов,
    # по которым он хочет видеть свои баллы
    await message.answer(
        text=LEXICON["discipline_rating"],
        reply_markup=kb.discipline_rating(disciplines=disciplines)
    )


# Отправка рейтинга по дисциплине
@router.message(DisciplineFilter(disciplines=disciplines))
async def send_discipline_rating(message: Message):
    msg = await message.answer(text=LEXICON["processing"])

    discipline = message.text[1:]  # Убираем 📌 из текста

    # Сохраняем в переменную объект RatingParser
    # и вызываем метод для загрузки баллов по выбранному предмету
    discipline_rating = users_data[message.chat.id]["data"]["rating"]
    discipline_rating = await discipline_rating.discipline_rating(discipline)

    # Отправляем баллы по выбранному предмету
    await msg.edit_text(text=discipline_rating)


# Отправка краткого рейтинга
@router.message(F.text == LEXICON_COMMANDS["short_rating"])
async def send_short_rating(message: Message):
    msg = await message.answer(text=LEXICON["processing"])

    # Сохраняем в переменную объект RatingParser
    # и вызываем метод для загрузки краткой информации по баллам предметов
    rating = users_data[message.chat.id]["data"]["rating"]
    rating = await rating.short_disciplines_rating

    # Отправляем краткую информацию по баллам предметов
    await msg.edit_text(text=rating)


# Отправка полного рейтинга с пагинацией
@router.message(F.text == LEXICON_COMMANDS["full_rating"])
async def send_full_rating(message: Message):
    global rating_list
    global pages

    await message.answer(LEXICON["processing"])

    # Сохраняем в переменную объект RatingParser
    # и вызываем метод для загрузки баллов по всем предметам
    rating = users_data[message.chat.id]["data"]["rating"]
    rating_list = await rating.full_disciplines_rating

    # Формируем номера страниц и записываем текущую
    pages = [str(i) for i in range(1, len(rating_list) + 1)]
    page = users_data[message.chat.id]["data"]["rating_page"]

    # Пагинация в зависимости от текущей страницы
    if page != len(pages) - 1 and page != 0:
        await message.answer(
            text=rating_list[page],
            reply_markup=create_pagination_keyboard(
                "backward_rating", pages[page], "forward_rating"
            )
        )
    elif page == 0:
        await message.answer(
            text=rating_list[page],
            reply_markup=create_pagination_keyboard(
                pages[page], "forward_rating"
            )
        )
    else:
        await message.answer(
            text=rating_list[page],
            reply_markup=create_pagination_keyboard(
                "backward_rating", pages[page]
            )
        )


# Обработка кнопки ">>" для рейтинга
@router.callback_query(F.data == "forward_rating")
async def press_forward_rating(callback: CallbackQuery):
    global rating_list
    global pages

    # Текущая страница
    page = users_data[callback.from_user.id]["data"]["rating_page"]

    # Пагинация в зависимости от текущей страницы
    if page + 1 < len(pages) - 1:
        await callback.message.edit_text(
            text=rating_list[page + 1],
            reply_markup=create_pagination_keyboard(
                "backward_rating", pages[page + 1], "forward_rating"
            )
        )
    else:
        await callback.message.edit_text(
            text=rating_list[page + 1],
            reply_markup=create_pagination_keyboard(
                "backward_rating", pages[page + 1]
            )
        )

    # Сохраняем в базу, что пользователь перешёл на следующую страницу
    users_data[callback.from_user.id]["data"]["rating_page"] += 1

    await callback.answer()


# Обработка кнопки "<<" для рейтинга
@router.callback_query(F.data == "backward_rating")
async def press_backward_rating(callback: CallbackQuery):
    global rating_list
    global pages

    # Текущая страница
    page = users_data[callback.from_user.id]["data"]["rating_page"]

    # Пагинация в зависимости от текущей страницы
    if page - 1 > 0:
        await callback.message.edit_text(
            text=rating_list[page - 1],
            reply_markup=create_pagination_keyboard(
                "backward_rating", pages[page - 1], "forward_rating"
            )
        )
    else:
        await callback.message.edit_text(
            text=rating_list[page - 1],
            reply_markup=create_pagination_keyboard(
                pages[page - 1], "forward_rating"
            )
        )

    # Сохраняем в базу, что пользователь перешёл на предыдущую страницу
    users_data[callback.from_user.id]["data"]["rating_page"] -= 1

    await callback.answer()


# Обновление рейтинга пользователя
@router.message(F.text == LEXICON_COMMANDS["update_rating"])
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
    users_data[message.chat.id]["data"]["account"].update_student_data(key="rating")

    await msg.edit_text(text=LEXICON["successful_updating"])
