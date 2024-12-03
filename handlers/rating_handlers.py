# Импорты пользовательских модулей
import keyboards.menu_kb as kb
from keyboards.pagination_kb import create_pagination_keyboard

from config_data.config import load_config

from cipher import PassCipher

# Импорт инициализатора таблиц БД, словарь для хранения страниц и типы
from database import initialize_databases, users_data
from database import WeeklySchedule, Grades, Users

from filters import DisciplineFilter

from student_account import StudentAccount

from lexicon import LEXICON, LEXICON_COMMANDS, COMPONENTS, ATTESTATION

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

# Инициализируем кортеж с таблицами
tables: tuple[Users, Grades, WeeklySchedule] = ()


# Меню баллов БРС
@router.message(F.text == LEXICON_COMMANDS["rating"])
async def rating_menu(message: Message):
    global tables
    global disciplines

    tables = await initialize_databases()

    if not disciplines:
        grades_table = tables[1]

        # Формируем список дисциплин
        data = await grades_table.select_name_subjects(
            chat_id=message.chat.id
        )
        disciplines.extend([f"📌{i}" for i in data])

    # Отправляем пользователю меню с кнопками для работы с баллами
    await message.answer(
        text=LEXICON["rating"],
        reply_markup=kb.RatingMenu
    )


# Меню баллов по дисциплинам
@router.message(F.text == LEXICON_COMMANDS["discipline_rating"])
async def discipline_rating_menu(message: Message):
    global disciplines
    global tables

    await message.answer(text=LEXICON["processing"])

    # Отправляем пользователю меню с выбором предметов,
    # по которым он хочет видеть свои баллы
    await message.answer(
        text=LEXICON["discipline_rating"],
        reply_markup=kb.discipline_rating(disciplines=disciplines)
    )


# Отправка рейтинга по дисциплине
@router.message(DisciplineFilter(disciplines=disciplines))
async def send_discipline_rating(message: Message):
    global tables

    grades_table = tables[1]

    msg = await message.answer(text=LEXICON["processing"])

    _, discipline_rating = await grades_table.select_grades(
        chat_id=message.chat.id,
        subject=message.text[1:]
    )

    text = f"{message.text}:\n"
    for component, score in discipline_rating:
        if component in COMPONENTS:
            text += f"\nℹ️*{component}*: `{score}`\n\n"
        elif component in ATTESTATION.values():
            if component == ATTESTATION["Current"]:
                text += f"*{component}*: `{score}`\n\n"
            else:
                text += f"\n*{component}*: `{score}`\n\n"
        else:
            text += f"{'\u00A0' * 4}— {component}: `{score}`\n"

    # Отправляем баллы по выбранному предмету
    await msg.edit_text(text=text, parse_mode="Markdown")


# Отправка краткого рейтинга
@router.message(F.text == LEXICON_COMMANDS["short_rating"])
async def send_short_rating(message: Message):
    global tables
    global disciplines

    msg = await message.answer(text=LEXICON["processing"])

    grades_table = tables[1]

    text = ""
    for subject in disciplines:
        text += f"{subject}:\n"
        _, scores = await grades_table.select_grades(
            chat_id=message.chat.id,
            subject=subject[1:]
        )
        component, score = scores[0]
        text += f"{component}: {score}\n\n"

    # Отправляем краткую информацию по баллам предметов
    await msg.edit_text(text=text, parse_mode="Markdown")


# Отправка полного рейтинга с пагинацией
@router.message(F.text == LEXICON_COMMANDS["full_rating"])
async def send_full_rating(message: Message):
    global rating_list
    global pages
    global tables
    global disciplines

    await message.answer(LEXICON["processing"])

    grades_table = tables[1]

    for subject in disciplines:
        text = f"{subject}:\n"
        _, scores = await grades_table.select_grades(
            chat_id=message.chat.id,
            subject=subject[1:]
        )
        for component, score in scores:
            if component in COMPONENTS:
                text += f"\nℹ️*{component}*: `{score}`\n\n"
            elif component in ATTESTATION.values():
                if component == ATTESTATION["Current"]:
                    text += f"*{component}*: `{score}`\n\n"
                else:
                    text += f"\n*{component}*: `{score}`\n\n"
            else:
                text += f"{'\u00A0' * 4}— {component}: `{score}`\n"

        text += "\n"
        rating_list.append(text)

    # Формируем номера страниц и записываем текущую
    pages = [str(i) for i in range(1, len(disciplines) + 1)]
    page = users_data[message.chat.id]["rating_page"]

    # Пагинация в зависимости от текущей страницы
    if page != len(pages) - 1 and page != 0:
        await message.answer(
            text=rating_list[page],
            parse_mode="Markdown",
            reply_markup=create_pagination_keyboard(
                "backward_rating", pages[page], "forward_rating"
            )
        )
    elif page == 0:
        await message.answer(
            text=rating_list[page],
            parse_mode="Markdown",
            reply_markup=create_pagination_keyboard(
                pages[page], "forward_rating"
            )
        )
    else:
        await message.answer(
            text=rating_list[page],
            parse_mode="Markdown",
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
    page = users_data[callback.from_user.id]["rating_page"]

    # Пагинация в зависимости от текущей страницы
    if page + 1 < len(pages) - 1:
        await callback.message.edit_text(
            text=rating_list[page + 1],
            parse_mode="Markdown",
            reply_markup=create_pagination_keyboard(
                "backward_rating", pages[page + 1], "forward_rating"
            )
        )
    else:
        await callback.message.edit_text(
            text=rating_list[page + 1],
            parse_mode="Markdown",
            reply_markup=create_pagination_keyboard(
                "backward_rating", pages[page + 1]
            )
        )

    # Сохраняем в базу, что пользователь перешёл на следующую страницу
    users_data[callback.from_user.id]["rating_page"] += 1

    await callback.answer()


# Обработка кнопки "<<" для рейтинга
@router.callback_query(F.data == "backward_rating")
async def press_backward_rating(callback: CallbackQuery):
    global rating_list
    global pages

    # Текущая страница
    page = users_data[callback.from_user.id]["rating_page"]

    # Пагинация в зависимости от текущей страницы
    if page - 1 > 0:
        await callback.message.edit_text(
            text=rating_list[page - 1],
            parse_mode="Markdown",
            reply_markup=create_pagination_keyboard(
                "backward_rating", pages[page - 1], "forward_rating"
            )
        )
    else:
        await callback.message.edit_text(
            text=rating_list[page - 1],
            parse_mode="Markdown",
            reply_markup=create_pagination_keyboard(
                pages[page - 1], "forward_rating"
            )
        )

    # Сохраняем в базу, что пользователь перешёл на предыдущую страницу
    users_data[callback.from_user.id]["rating_page"] -= 1

    await callback.answer()


# Обновление рейтинга пользователя
@router.message(F.text == LEXICON_COMMANDS["update_rating"])
async def update_student_rating(message: Message):
    global tables

    users_table = tables[0]

    msg = await message.answer(text=LEXICON["processing"])

    # Записываем логин и пароль пользователя
    # Пароль дешифруем для авторизации
    login, password, _ = await users_table.select_user_data(
        chat_id=message.chat.id
    )
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

    await account.rating.full_disciplines_rating(key="update")

    await msg.edit_text(text=LEXICON["successful_updating"])
