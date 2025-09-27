# Телеграм-бот для студентов УрФУ, который скидывает расписание на текущую неделю и баллы БРС.

## Краткое описание.

- Бот подключается к личному кабинету студента через авторизацию по паролю и логину, откуда парсит расписание и баллы БРС.
- Парсинг происходит с помощью Selenium.WebDriver'а, который запускает браузер и имитирует действия пользователя на сайте для прогрузки Java-скриптов.
- [Selenoid](https://github.com/aerokube/selenoid) изолированно запускает браузеры в Docker-контейнерах, что позволяет параллельно работать с несколькими браузерами.
- Все данные бот хранит в БД, код которой в database/database.sql

## Установка

### Локальная установка

**1. Склонируйте репозиторий:**
```bash
git clone https://github.com/mikryukoff/StudentBot.git
cd StudentBot
```

**2. Создайте виртуальное окружение и активируйте его:**

- Для Linux/macOS:
```bash
python -m venv venv
source venv/bin/activate
venv\Scripts\activate
```

- Для Windows:
```bash
python -m venv venv
source venv\Scripts\activate
```

**3. Установите зависимости:**
```bash
pip install -r requirements.txt
```

**4. Установите базу данных SQL. Запустите запрос из database/database.sql**

**5. Создайте файл .env в корне проекта с необходимыми переменными окружения (пример ниже).**

## Настройка

### Переменные окружения

- Для работы бота необходимы следующие переменные окружения, которые нужно указать в файле .env:
```makefile
BOT_TOKEN="4342342335:AAfwmfdlkIJLKSFjlkd_234adwalkWLKJ"                         # Токен телеграм-бота
SELENOID_URL="http://localhost:4444/wd/hub"                                      # URL для подключения к Selenoid
SECRET_KEY="ymkc933zy9wtafyy4e8gedf5c7hixawnivqhlo7d4iykfbf6rkip9l731zetq7o0"    # Секретный ключ для шифрования паролей (64 бит)
API_URL="http://backend:8000"                                                    # URL для отправки запроса на API
DB_HOST="host.docker.internal"                                                   # Хост БД 
DB_USER="root"                                                                   # Имя администратора БД
DB_PASSWORD=""                                                                   # Пароль от БД
DB_NAME="db_bot"                                                                 # Название БД
```

### Настройка [Selenoid'а](https://github.com/aerokube/selenoid) и WebDriver'а:

- Настройки для [Selenoid'а](https://github.com/aerokube/selenoid) и WebDriver'а лежат в папке config_data в файле config.py.

## Запуск

### Сборка и запуск Docker'а:

- Сборка и запуск:
```bash
docker-compose up --build -d
```

- Убедитесь, что образ Chrome существует:
```bash
docker pull selenoid/vnc_chrome:125.0
```

- Проверка работы:
```bash
docker logs student-bot
```

## Схема каталогов проекта

```plaintext
StudentBot/
├── cipher/                         # Модули для шифрования данных
│   ├── __init__.py                 # Инициализация пакета
│   └── cipher.py                   # Реализация функций шифрования
├── config_data/                    # Файлы конфигурации
│   └── config.py                   # Основные настройки приложения
├── database/                       # Хранение данных
│   ├── __init__.py                 # Инициализация пакета
│   └── database.py                 # Реализация БД
├── filters/                        # Фильтры для обработки данных
│   ├── __init__.py                 # Инициализация пакета
│   └── filters.py                  # Реализация фильтров
├── handlers/                       # Обработчики событий
|   ├── auth_handlers.py            # Обработчик авторизации
|   ├── menu_handlers.py            # Обработчик стартового меню
|   ├── rating_handlers.py          # Обработчик работы с баллами
|   └── schedule_handlers.py        # Обработчик работы с расписанием
├── keyboards/                      # Пользовательские клавиатуры
│   ├── menu_kb.py                  # Определение кнопок меню
|   └── pagination_kb.py            # Определение пагинации
├── lexicon/                        # Каталог команд
│   ├── __init__.py                 # Инициализация пакета
│   └── lexicon.py                  # Команды и ответы бота
├── rating_parser/                  # Парсинг рейтингов
│   ├── __init__.py                 # Инициализация пакета
│   └── rating_parser.py            # Парсер баллов БРС
├── schedule_parser/                # Парсинг расписания
│   ├── __init__.py                 # Инициализация пакета
│   └── schedule_parser.py          # Парсер расписания
├── selenoid/                       # Конфигурация Selenoid
│   └── config/                     # Настройки Selenoid
│       ├── browsers.json           # Настройки браузеров для Selenoid
├── student_account/                # Инициализатор драйвера Selenium
│   ├── __init__.py                 # Инициализация пакета
│   ├── exceptions.py               # Вспомогательные исключения
│   └── student_account.py          # Драйвер Selenium с настройками и авторизацией
├── __main__.py                     # Основной исполняемый файл бота
├── .env.example                    # Пример файла с переменными окружения
├── .gitignore                      # Файлы и каталоги, игнорируемые Git
├── docker-compose.yaml             # Конфигурация для Docker Compose
├── Dockerfile                      # Инструкция для сборки Docker-образа
├── README.md                       # Описание проекта
└── requirements.txt                # Список зависимостей проекта
```


## Контакты

### Реализация бота:

- Автор: Микрюков Денис Алексеевич РИ-230931
- telegram: https://t.me/mikryukoff17
- VK: https://vk.com/mikryukoff17
- Email: den20011709@gmail.com

### Реализация базы данных:

- Автор: Рябов Михаил Сергеевич РИ-230916
- telegram: https://t.me/not_ryaba
- Email: not_ryaba@gmail.com
- GitHub: https://github.com/ryabov3