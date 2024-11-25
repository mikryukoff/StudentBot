# Базовый образ
FROM python:3.13

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Установка зависимостей
RUN pip install --no-cache-dir -r requirements.txt

# Копирование программы
COPY __main__.py /app/main.py
WORKDIR /app

RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser

# Команда запуска
CMD ["python", "-m", "__main__"]
