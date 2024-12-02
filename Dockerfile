# Базовый образ с Python 3.13
FROM python:3.13-slim

# Отключение .pyc файлов и включение небуферизованного вывода
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Установка локалей
RUN apt-get update && apt-get install -y locales && \
    echo "ru_RU.UTF-8 UTF-8" > /etc/locale.gen && \
    locale-gen && \
    update-locale LANG=ru_RU.UTF-8

# Установка переменных окружения для локали
ENV LANG ru_RU.UTF-8
ENV LANGUAGE ru_RU:ru
ENV LC_ALL ru_RU.UTF-8

# Рабочая директория внутри контейнера
WORKDIR /app

# Копирование файла requirements.txt
COPY requirements.txt /app/

# Установка зависимостей
RUN pip install --no-cache-dir -r requirements.txt

# Копирование остальных файлов проекта
COPY . /app/

# Запуск приложения через __main__.py
CMD ["python", "/app/__main__.py"]