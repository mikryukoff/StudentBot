from datetime import datetime, timedelta
from typing import Union
from urllib.parse import unquote

from app.cipher import PassCipher
from app.database import Grades, Users, WeeklySchedule, initialize_databases
from app.exception_handlers import (
    global_exception_handler,
    invalid_credentials_handler,
    user_not_found_exc_handler,
    validation_exception_handler,
)
from app.exceptions import (
    InvalidCredentialsException,
    UserNotFoundException,
    ValidationException,
)
from app.models import (
    InvalidCredentialsExceptionModel,
    RequestValidationErrorModel,
    User,
    UserInDB,
    UserNotFoundExceptionModel,
)
from app.parsers.exceptions import IncorrectDataException
from app.parsers.student_account import StudentAccount
from fastapi import BackgroundTasks, FastAPI, status

from config import load_config

app = FastAPI()

app.add_exception_handler(Exception, global_exception_handler)
app.add_exception_handler(ValidationException, validation_exception_handler)

app.add_exception_handler(InvalidCredentialsException, invalid_credentials_handler)
app.add_exception_handler(UserNotFoundException, user_not_found_exc_handler)


async def update_table(user_id: int, table: str):
    users_table: Users = await get_table("users")
    config = load_config()
    cipher: PassCipher = PassCipher(config.user_data.secret_key)

    if not await users_table.is_user_in_db(user_id):
        raise UserNotFoundException(user_id=user_id)

    # Записываем логин и пароль пользователя
    # Пароль дешифруем для авторизации
    login, password, _ = await users_table.select_user_data(
        chat_id=user_id
    )
    password = cipher.decrypt_password(password)

    try:
        account: StudentAccount = await StudentAccount(
            user_login=login,
            user_pass=password,
            chat_id=user_id
        ).driver

    except IncorrectDataException:
        raise InvalidCredentialsException()

    if table == "schedule":
        await account.schedule.week_schedule(key="update")
    elif table == "rating":
        await account.rating.full_disciplines_rating(key="update")

    return account


async def get_table(table_name: str | tuple) -> Union[Users, Grades, WeeklySchedule]:
    """
    table_name: 
                types: str | tuple;
                description: название таблицы или кортеж, если нужно несколько;
                values: 'users', 'grades', 'schedule'.
    """
    table_types = {
        "users": 0,
        "grades": 1,
        "schedule": 2
    }
    tables = await initialize_databases()

    if isinstance(table_name, tuple):
        return tuple(tables[table_types[i]] for i in table_name)
    return tables[table_types[table_name]]

#----------------------------------------------------------------------------------------#

@app.post(
    "/users/authorization",
    responses={
        status.HTTP_200_OK: {"message": "Successful authorization."},
        status.HTTP_401_UNAUTHORIZED: {"model": InvalidCredentialsExceptionModel},
        status.HTTP_422_UNPROCESSABLE_CONTENT: {"model": RequestValidationErrorModel}
    }
)
async def authorization(user: User, background_tasks: BackgroundTasks):
    users_table: User = await get_table("users")
    config = load_config()
    cipher: PassCipher = PassCipher(config.user_data.secret_key)
    account: StudentAccount = None

    try:
        account: StudentAccount = await StudentAccount(
            user_login=user.email,
            user_pass=user.password,
            chat_id=user.user_id
        ).driver

    except IncorrectDataException:
        raise InvalidCredentialsException()

    # Получаем текущую дату
    today = datetime.today()

    # Находим начало недели (понедельник)
    week_start = today - timedelta(days=today.weekday())

    # Если пользователь успешно авторизовался, добавляем его в БД
    await users_table.add_user_in_table(
        chat_id=user.user_id,
        login=user.email,
        password_hash=cipher.encrypt_password(user.password),
        current_week_start=week_start.strftime('%Y-%m-%d')
    )

    # Записываем все данные пользователя в БД
    await account.schedule.week_schedule(key="insert")
    await account.rating.full_disciplines_rating(key="insert")

    background_tasks.add_task(account.browser.close)
    background_tasks.add_task(account.browser.quit)


@app.get(
    "/users/{user_id}",
    responses={
        status.HTTP_200_OK: {"model": UserInDB},
        status.HTTP_404_NOT_FOUND: {"model": UserNotFoundExceptionModel}
    }
)
async def get_user_data(user_id: int):
    users_table: User = await get_table("users")

    if not await users_table.is_user_in_db(user_id):
        raise UserNotFoundException(user_id=user_id)

    email, hash_pass, week_start_date = await users_table.select_user_data(user_id)

    return UserInDB(email=email, hashed_password=hash_pass, user_id=user_id, week_start_date=week_start_date)

#----------------------------------------------------------------------------------------#

@app.get(
    "/disciplines/{user_id}",
    responses={
        status.HTTP_404_NOT_FOUND: {"model": UserNotFoundExceptionModel}
    }
)
async def get_user_disciplines(user_id: int):
    grades_table, users_table = await get_table(("grades", "users"))
    grades_table: Grades
    users_table: Users

    if not await users_table.is_user_in_db(user_id):
        raise UserNotFoundException(user_id=user_id)

    disciplines = await grades_table.select_name_subjects(
        chat_id=user_id
    )

    return disciplines


@app.get(
    "/disciplines/{user_id}/rating",
    responses={
        status.HTTP_404_NOT_FOUND: {"model": UserNotFoundExceptionModel}
    }
)
async def get_discipline_rating(user_id: int, discipline: str):
    grades_table, users_table = await get_table(("grades", "users"))
    grades_table: Grades
    users_table: Users

    if not await users_table.is_user_in_db(user_id):
        raise UserNotFoundException(user_id=user_id)
        
    discipline = unquote(discipline)

    _, discipline_rating = await grades_table.select_grades(
        chat_id=user_id,
        subject=discipline
    )

    return discipline_rating


@app.put(
    "/disciplines/{user_id}",
    responses={
        status.HTTP_404_NOT_FOUND: {"model": UserNotFoundExceptionModel},
        status.HTTP_401_UNAUTHORIZED: {"model": InvalidCredentialsExceptionModel},
        status.HTTP_422_UNPROCESSABLE_CONTENT: {"model": RequestValidationErrorModel}
    }
)
async def update_discipline_rating(user_id: int, background_tasks: BackgroundTasks):
    account = await update_table(user_id, table="rating")
    background_tasks.add_task(account.browser.close)
    background_tasks.add_task(account.browser.quit)

#----------------------------------------------------------------------------------------#

@app.get("/schedule/{user_id}")
async def get_day_schedule(user_id: int, day: int):
    schedule_table, users_table = await get_table(("schedule", "users"))
    schedule_table: WeeklySchedule
    users_table: User

    if not await users_table.is_user_in_db(user_id):
        raise UserNotFoundException(user_id=user_id)

    _, data = await schedule_table.select_discipline(
        chat_id=user_id,
        day_of_week=day
    )

    return data


@app.put(
    "/schedule/{user_id}",
    responses={
        status.HTTP_404_NOT_FOUND: {"model": UserNotFoundExceptionModel},
        status.HTTP_401_UNAUTHORIZED: {"model": InvalidCredentialsExceptionModel},
        status.HTTP_422_UNPROCESSABLE_CONTENT: {"model": RequestValidationErrorModel}
    }
)
async def update_week_schedule(user_id: int, background_tasks: BackgroundTasks):
    account = await update_table(user_id, table="schedule")
    background_tasks.add_task(account.browser.close)
    background_tasks.add_task(account.browser.quit)

#----------------------------------------------------------------------------------------#