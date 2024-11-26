# Базовый образ с Python 3.13
FROM python:3.13-slim

# Отключение .pyc файлов и включение небуферизованного вывода
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Рабочая директория внутри контейнера
WORKDIR /app

# Копирование файла requirements.txt
COPY requirements.txt /app/

# Установка зависимостей
RUN pip install --no-cache-dir -r requirements.txt

# Копирование остальных файлов проекта
COPY . /app/

# Запуск приложения через __main__.py
CMD ["python", "-m", "__main__"]
