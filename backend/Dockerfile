# Используем официальный Python образ
FROM python:3.11-alpine

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы зависимостей
COPY backend/pyproject.toml backend/uv.lock ./

# Устанавливаем uv (если не установлен в образе)
RUN pip install --no-cache-dir uv

# Устанавливаем зависимости
RUN uv sync --frozen --no-dev

# Копируем исходный код
COPY backend/app/ ./app/
COPY config/ ./config/

# Создаем симлинк для доступа к конфигурации
RUN ln -sf /app/config /app/app/config

# Открываем порт
EXPOSE 8000

ENV PYTHONPATH=/app

# Запускаем приложение
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]