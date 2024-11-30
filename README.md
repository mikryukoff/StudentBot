# README

## Телеграм-бот для студентов УрФУ, который умеет скидывать расписание на текущую неделю и текущие баллы БРС.

- Все необходимые модули лежат в requirements.txt.
- Необходимые переменные окружения лежат в .env.example.
- Бот хранит данные в json файлах в папке database.
- Бот работает через [Selenoid](https://github.com/aerokube/selenoid), который изолированно запускает браузеры в Docker-контейнерах.
- Браузеры работают с помощью Selenium.WebDriver'а.

## Запуск [Selenoid'а](https://github.com/aerokube/selenoid):

**Если вы работаете на Linux (обычный сервер или виртуальная машина):**  
```bash
tools/cm_linux_amd64 selenoid start --vnc --tmpfs 128
```

**Если работаете на macOS:**

- Для Intel-процессоров:  
```bash
tools/cm_darwin_amd64 selenoid start --vnc --tmpfs 128
```

- Для Apple Silicon (M1/M2):  
```bash
tools/cm_darwin_arm64 selenoid start --vnc --tmpfs 128
```

**Если работаете на Windows:**

- Для 32-битной версии Windows:   
```bash
tools/cm_windows_386.exe selenoid start --vnc --tmpfs 128
```

- Для 64-битной версии Windows:  
```bash
tools/cm_windows_amd64.exe selenoid start --vnc --tmpfs 128
```

## Сборка и запуск Docker'а:

**Сборка и запуск:**
```bash
docker-compose up --build -d
```

**Убедитесь, что образ Chrome существует:**
```bash
docker pull selenoid/vnc_chrome:128.0
```

**Проверка работы:**
```bash
docker logs student-bot
```

## Настройка [Selenoid'а](https://github.com/aerokube/selenoid) и WebDriver'а:

- Настройки для [Selenoid'а](https://github.com/aerokube/selenoid) и WebDriver'а лежат в папке config_data в файле config.py.

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
├── tools/                          # Установщики Selenoid
│   ├── cm_linux_amd64              # Утилита для Linux
│   ├── cm_darwin_amd64             # Утилита для macOS (Intel)
│   ├── cm_darwin_arm64             # Утилита для macOS (M1/M2)
│   └── cm_windows_amd64.exe        # Утилита для Windows
├── __main__.py                     # Основной исполняемый файл бота
├── .env.example                    # Пример файла с переменными окружения
├── .gitignore                      # Файлы и каталоги, игнорируемые Git
├── docker-compose.yaml             # Конфигурация для Docker Compose
├── Dockerfile                      # Инструкция для сборки Docker-образа
├── README.md                       # Описание проекта
└── requirements.txt                # Список зависимостей проекта
```