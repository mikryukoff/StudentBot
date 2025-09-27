# Используем официальный Python образ
FROM python:3.11-alpine

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы зависимостей
COPY frontend/pyproject.toml frontend/uv.lock ./

# Устанавливаем uv (если не установлен в образе)
RUN pip install --no-cache-dir uv

# Устанавливаем зависимости
RUN uv sync --frozen --no-dev

# Копируем исходный код
COPY frontend/bot/ ./bot/
COPY config/ ./config/

# Создаем симлинк для доступа к конфигурации
RUN ln -sf /app/config /app/bot/config

# Открываем порт
EXPOSE 5000

ENV PYTHONPATH=/app

# Запускаем бота
CMD ["uv", "run", "python", "-m", "bot"]