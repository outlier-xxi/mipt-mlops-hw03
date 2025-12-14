FROM python:3.11-slim

WORKDIR /app

# Устанавливаем uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

COPY pyproject.toml uv.lock ./
COPY app/ ./app/

# Устанавливаем зависимости
RUN uv sync --frozen

CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

