import aiomysql
from common.config import load_config, Config
from typing import Union


# Определяем конфиг
config: Config = load_config()

# Определяем словарь для работы с обектами каждого пользователя
users_data: dict = {}


class Table:
    def __init__(self, host: str, user: str, password: str, db_name: str):
        """
        Инициализирует класс Table и устанавливает параметры подключения к базе данных.

        Аргументы:
            host (str): Хост базы данных.
            user (str): Имя пользователя для подключения.
            password (str): Пароль для подключения.
            db_name (str): Имя базы данных.
        """
        self.host = host
        self.user = user
        self.password = password
        self.db_name = db_name

    async def connect(self) -> None:
        """
        Создает пул соединений с базой данных.
        """
        self.connection_pool = await aiomysql.create_pool(
            host=self.host,
            user=self.user,
            password=self.password,
            db=self.db_name,
            autocommit=True,
        )

    async def close(self) -> None:
        """
        Закрывает пул соединений с базой данных.
        """
        if self.connection_pool:
            self.connection_pool.close()
            await self.connection_pool.wait_closed()


class Users(Table):
    async def is_user_in_db(self, chat_id: int) -> bool:
        """
        Проверяет, существует ли пользователь с указанным chat_id в базе данных.

        Аргументы:
            chat_id (int): Идентификатор чата пользователя.

        Возвращает:
            bool: True, если пользователь существует, иначе False.
        """
        async with self.connection_pool.acquire() as connection:
            async with connection.cursor() as cursor:
                select_user = f"SELECT * FROM users WHERE chat_id = {chat_id};"
                await cursor.execute(select_user)
                rows = await cursor.fetchone()
            return True if rows else False

    async def add_user_in_table(
        self, chat_id: int, login: str, password_hash: str, current_week_start: str
    ) -> None:
        """
        Добавляет нового пользователя в таблицу Users.

        Аргументы:
            chat_id (int): Идентификатор чата пользователя.
            login (str): Логин пользователя.
            password_hash (str): Хэш пароля пользователя.
            current_week_start (str): Дата начала текущей недели.
        """
        async with self.connection_pool.acquire() as connection:
            async with connection.cursor() as cursor:
                insert_user_data = f"""
                    INSERT INTO users (chat_id, login, password_hash, current_week_start)
                    VALUES ({chat_id}, '{login}', '{password_hash}', '{current_week_start}');
                """
                await cursor.execute(insert_user_data)

    async def delete_user(self, chat_id: int) -> None:
        """
        Удаляет пользователя с указанным chat_id из базы данных.

        Аргументы:
            chat_id (int): Идентификатор чата пользователя.
        """
        async with self.connection_pool.acquire() as connection:
            async with connection.cursor() as cursor:
                delete_user = f"DELETE FROM users WHERE chat_id = {chat_id};"
                await cursor.execute(delete_user)

    async def select_user_data(self, chat_id: int) -> tuple[str, str, str]:
        """
        Получает данные пользователя по его chat_id.

        Аргументы:
            chat_id (int): Идентификатор чата пользователя.

        Возвращает:
            tuple[str, str, str]: Логин, хэш пароля и дата начала текущей недели.

        Исключение:
            ValueError: Если пользователь с указанным chat_id не найден.
        """
        async with self.connection_pool.acquire() as connection:
            async with connection.cursor() as cursor:
                select = f"""
                    SELECT login, password_hash, current_week_start
                    FROM users
                    WHERE chat_id = {chat_id};
                """
                await cursor.execute(select)
                row = await cursor.fetchone()

        if not row:
            raise ValueError(f"Пользователь с chat_id {chat_id} не найден.")

        login, password_hash, current_week_start = row

        return login, password_hash, current_week_start

    async def update_chat_id(self, chat_id: int, login: str) -> None:
        """
        Обновляет идентификатор чата для указанного логина.

        Аргументы:
            chat_id (int): Новый идентификатор чата пользователя.
            login (str): Логин пользователя.
        """
        async with self.connection_pool.acquire() as connection:
            async with connection.cursor() as cursor:
                update_chat_id = f"""
                    UPDATE users
                    SET chat_id = {chat_id}
                    WHERE login = '{login}';
                """
                await cursor.execute(update_chat_id)

    async def update_current_date(self, current_week_start: str) -> None:
        """
        Обновляет дату начала текущей недели для всех пользователей.

        Аргументы:
            current_week_start (str): Новая дата начала текущей недели.
        """
        async with self.connection_pool.acquire() as connection:
            async with connection.cursor() as cursor:
                update_user_data = f"""
                    UPDATE users
                    SET current_week_start = '{current_week_start}';
                """
                await cursor.execute(update_user_data)


class Grades(Table):
    async def insert_subject(
        self, chat_id: int, subject: str, component: str, score: str
    ) -> None:
        """
        Добавляет новую запись о предмете в таблицу Grades.

        Аргументы:
            chat_id (int): Идентификатор чата пользователя.
            subject (str): Название предмета.
            component (str): Компонент оценки (например, контрольная работа).
            score (str): Оценка.
        """
        async with self.connection_pool.acquire() as connection:
            async with connection.cursor() as cursor:
                insert_subject = f"""
                    INSERT INTO Grades (chat_id, subject, component, score)
                    VALUES ({chat_id}, '{subject}', '{component}', '{score}');
                """
                await cursor.execute(insert_subject)

    async def select_name_subjects(self, chat_id: int) -> list[str]:
        """
        Получает список уникальных названий предметов для указанного пользователя.

        Аргументы:
            chat_id (int): Идентификатор пользователя, для которого необходимо получить список предметов.

        Возвращает:
            list[str]: Список уникальных названий предметов, связанных с указанным пользователем.
        """
        async with self.connection_pool.acquire() as connection:
            async with connection.cursor() as cursor:
                select = f"""
                    SELECT DISTINCT subject
                    FROM Grades
                    WHERE chat_id = {chat_id};
                """
                await cursor.execute(select)
                rows = await cursor.fetchall()
                name_subjects = [row[0] for row in rows]

            return name_subjects

    async def select_grades(
        self, chat_id: int, subject: str
    ) -> tuple[str, list[list[str, str]]]:
        """
        Получает оценки для указанного пользователя и предмета.

        Аргументы:
            chat_id (int): Идентификатор чата пользователя.
            subject (str): Название предмета.

        Возвращает:
            tuple[str, list[list[str, str]]]: Название предмета и список компонентов с оценками.
        """
        async with self.connection_pool.acquire() as connection:
            async with connection.cursor() as cursor:
                select_grade = f"""
                    SELECT subject, component, score
                    FROM Grades
                    WHERE chat_id = {chat_id} and subject = '{subject}';
                """
                await cursor.execute(select_grade)
                rows = await cursor.fetchall()

                name_discipline = rows[0][0]
                component_score = [[row[1], row[2]] for row in rows]

                return name_discipline, component_score

    async def update_grades(
        self, chat_id: int, subject: str, component: str, score: str
    ) -> None:
        """
        Обновляет оценку для указанного пользователя и предмета.

        Аргументы:
            chat_id (int): Идентификатор чата пользователя.
            subject (str): Название предмета.
            component (str): Компонент оценки (например, контрольная работа).
            score (str): Новая оценка.
        """
        async with self.connection_pool.acquire() as connection:
            async with connection.cursor() as cursor:
                update_grades = f"""
                    UPDATE Grades
                    SET score = '{score}'
                    WHERE chat_id = {chat_id} and
                        subject = '{subject}' and
                        component = '{component}';
                """
                await cursor.execute(update_grades)


class WeeklySchedule(Table):
    async def insert_discipline(
        self,
        chat_id: int,
        day_of_week: int,
        time_slot: str,
        subject: str,
        location: str,
    ) -> None:
        """
        Добавляет новую дисциплину в расписание.

        Аргументы:
            chat_id (int): Идентификатор чата пользователя.
            day_of_week (int): День недели (0 - понедельник, 6 - воскресенье).
            time_slot (str): Временной интервал.
            subject (str): Название предмета.
            location (str): Место проведения занятия.
        """
        async with self.connection_pool.acquire() as connection:
            async with connection.cursor() as cursor:
                insert_discipline = f"""
                    INSERT INTO WeeklySchedule (chat_id, day_of_week, time_slot, subject, location)
                    VALUES ({chat_id}, {day_of_week}, '{time_slot}', '{subject}', '{location}');
                """
                await cursor.execute(insert_discipline)

    async def select_discipline(
        self, chat_id: int, day_of_week: int
    ) -> tuple[int, list[list[Union[int, str]]]]:
        """
        Получает дисциплины для указанного пользователя и дня недели.

        Аргументы:
            chat_id (int): Идентификатор чата пользователя.
            day_of_week (int): День недели (0 - понедельник, 6 - воскресенье).

        Возвращает:
            tuple[int, list[list[Union[int, str]]]]: День недели и список дисциплин с временными интервалами и местами.
        """
        async with self.connection_pool.acquire() as connection:
            async with connection.cursor() as cursor:
                select_discipline = f"""
                    SELECT subject, time_slot, location, day_of_week
                    FROM WeeklySchedule
                    WHERE chat_id = {chat_id} and day_of_week = {day_of_week};
                """
                await cursor.execute(select_discipline)
                rows = await cursor.fetchall()
                results: list[list[Union[int, str]]] = []

                for row in rows:
                    results.append(
                        [
                            row[0],
                            row[1],
                            row[2],
                        ]
                    )

            return day_of_week, results

    async def update_discipline(
        self,
        chat_id: int,
        day_of_week: int,
        time_slot: str,
        subject: str,
        location: str,
    ) -> None:
        """
        Обновляет информацию о дисциплине для указанного пользователя и дня недели.

        Аргументы:
            chat_id (int): Идентификатор чата пользователя.
            day_of_week (int): День недели (0 - понедельник, 6 - воскресенье).
            time_slot (str): Временной интервал.
            subject (str): Название предмета.
            location (str): Место проведения занятия.
        """
        async with self.connection_pool.acquire() as connection:
            async with connection.cursor() as cursor:
                delete_day_data = f"""
                    DELETE FROM WeeklySchedule
                    WHERE chat_id = {chat_id} and
                    day_of_week = {day_of_week} and
                    time_slot = '{time_slot}';
                """
                await cursor.execute(delete_day_data)

        await self.insert_discipline(chat_id, day_of_week, time_slot, subject, location)


async def initialize_databases() -> tuple[Users, Grades, WeeklySchedule]:
    """
    Инициализирует соединения с базами данных для таблиц пользователей, оценок и расписания.

    Создает экземпляры классов `Users`, `Grades` и `WeeklySchedule`, устанавливает
    соединения с базами данных и возвращает их.

    Возвращает:
        tuple[Users, Grades, WeeklySchedule]: Кортеж, содержащий
        экземпляры классов `Users`, `Grades` и `WeeklySchedule`.
    """
    users_table = Users(
        config.database.host,
        config.database.user,
        config.database.password,
        config.database.db_name,
    )

    grades_table = Grades(
        config.database.host,
        config.database.user,
        config.database.password,
        config.database.db_name,
    )

    weekly_schedule_table = WeeklySchedule(
        config.database.host,
        config.database.user,
        config.database.password,
        config.database.db_name,
    )

    await users_table.connect()
    await grades_table.connect()
    await weekly_schedule_table.connect()

    return users_table, grades_table, weekly_schedule_table
