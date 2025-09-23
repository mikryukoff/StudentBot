FROM python:3.12.10-slim

WORKDIR /app

# Устанавливаем UV
RUN pip install uv

# Настройки окружения UV
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
ENV UV_TOOL_BIN_DIR=/usr/local/bin

# Копируем только зависимости бота
COPY bot/pyproject.toml bot/uv.lock ./
COPY common/pyproject.toml common/uv.lock ./common/

# Устанавливаем зависимости бота
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --no-dev

# Копируем исходный код бота (только нужные файлы)
COPY bot/src/ ./src/
COPY common/ ./common/

# Устанавливаем переменные окружения
ENV PATH="/app/.venv/bin:$PATH"

# Команда запуска
CMD ["uv", "run", "python", "src/__main__.py"]