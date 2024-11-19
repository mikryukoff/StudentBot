# README

## Телеграм-бот для студентов УрФУ, который умеет скидывать расписание на текущую неделю и текущие баллы БРС.

- Все необходимые модули лежат в requirements.txt.
- Необходимые переменные окружения лежат в .env.example.
- Бот хранит данные в json файлах в папке database.
- Бот работает через Selenoid, который изолированно запускает браузеры в Docker-контейнерах.
- Браузеры работают с помощью Selenium.WebDriver'а.

## Запуск Selenoid'а:

**Если вы работаете на Linux (обычный сервер или виртуальная машина):**  
```bash
$ tools/cm_linux_amd64 selenoid start --vnc --tmpfs 128
```

**Если работаете на macOS:**

- Для Intel-процессоров:  
```bash
$ tools/cm_darwin_amd64 selenoid start --vnc --tmpfs 128
```

- Для Apple Silicon (M1/M2):  
```bash
$ tools/cm_darwin_arm64 selenoid start --vnc --tmpfs 128
```

**Если работаете на Windows:**

- Для 32-битной версии Windows:   
```bash
$ tools/cm_windows_386.exe selenoid start --vnc --tmpfs 128
```

- Для 64-битной версии Windows:  
```bash
$ tools/cm_windows_amd64.exe selenoid start --vnc --tmpfs 128
```

## Настройка Selenoid'а и WebDriver'а:

- Настройки для Selenoid'а и WebDriver'а лежат в папке config_data в файле config.py.