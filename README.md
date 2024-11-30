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
├── cipher/
│   ├── init.py
│   └── cipher.py
├── config_data/
│   ├── init.py
│   └── config.py
├── database/
│   ├── init.py
│   └── data.json
├── filters/
│   ├── init.py
│   └── filters.py
├── handlers/
│   ├── init.py
│   └── handlers.py
├── keyboards/
│   ├── init.py
│   └── keyboards.py
├── lexicon/
│   ├── init.py
│   └── lexicon.py
├── rating_parser/
│   ├── init.py
│   └── parser.py
├── schedule_parser/
│   ├── init.py
│   └── parser.py
├── selenoid/
│   ├── config/
│   │   └── browsers.json
│   ├── cm_linux_amd64
│   ├── cm_darwin_amd64
│   ├── cm_darwin_arm64
│   └── cm_windows_amd64.exe
├── student_account/
│   ├── init.py
│   └── account.py
├── tools/
│   ├── init.py
│   └── tools.py
├── .env.example
├── .gitignore
├── Dockerfile
├── README.md
├── main.py
├── docker-compose.yaml
└── requirements.txt
```

**Описание схемы каталогов**

cipher/: модули для шифрования данных.
__init__.py: инициализация пакета.
cipher.py: реализация функций шифрования.
config_data/: файлы конфигурации.
__init__.py: инициализация пакета.
config.py: основные настройки приложения.
database/: хранение данных.
__init__.py: инициализация пакета.
data.json: файл с данными в формате JSON.
filters/: фильтры для обработки данных.
__init__.py: инициализация пакета.
filters.py: реализация фильтров.
handlers/: обработчики событий.
__init__.py: инициализация пакета.
handlers.py: обработка различных событий.
keyboards/: пользовательские клавиатуры.
__init__.py: инициализация пакета.
keyboards.py: определение клавиатур.
lexicon/: языковые ресурсы.
__init__.py: инициализация пакета.
lexicon.py: словари и текстовые ресурсы.
rating_parser/: парсинг рейтингов.
__init__.py: инициализация пакета.
parser.py: логика парсинга рейтингов.
schedule_parser/: парсинг расписания.
__init__.py: инициализация пакета.
parser.py: логика парсинга расписания.
selenoid/: конфигурация Selenoid.
config/:
browsers.json: настройки браузеров для Selenoid.
cm_linux_amd64: утилита для Linux.
cm_darwin_amd64: утилита для macOS (Intel).
cm_darwin_arm64: утилита для macOS (M1/M2).
cm_windows_amd64.exe: утилита для Windows.
student_account/: учетные записи студентов.
__init__.py: инициализация пакета.
account.py: управление учетными записями.
tools/: вспомогательные утилиты.
__init__.py: инициализация пакета.
tools.py: различные инструменты.
.env.example: пример файла с переменными окружения.
.gitignore: файлы и каталоги, игнорируемые Git.
Dockerfile: инструкция для сборки Docker-образа.
README.md: описание проекта.
__main__.py: основной исполняемый файл бота.
docker-compose.yaml: конфигурация для Docker Compose.
requirements.txt: список зависимостей проекта.
