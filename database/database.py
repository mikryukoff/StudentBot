from dataclasses import dataclass

import pymysql

users_data: dict = {}

@dataclass
class BotDB:
    host: str
    user: str
    password: str
    database: str

    try:
        connection = pymysql.connect(
            host="127.0.0.1",
            user='root',
            password='bUenMS0D',
            database="db_bot",
            cursorclass=pymysql.cursors.DictCursor
        )

        print("Connection good...")

        with connection.cursor() as cursor:
            insert_values = ("INSERT INTO Students (login)"
                            "VALUES ('Oleg2');")
            cursor.execute(insert_values)

        with connection.cursor() as cursor:
            select_all = ("SELECT *"
                        "FROM Students;")
            cursor.execute(select_all)
            rows = cursor.fetchall()
            for row in rows:
                print(row["login"])

    except Exception as _ex:
        print("Connection error...")
        print(_ex)
