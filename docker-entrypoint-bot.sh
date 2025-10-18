#!/bin/sh
set -e

echo "=== Starting Bot Entrypoint ==="

# Ждем немного, чтобы убедиться что volume смонтирован
sleep 1

# Выполняем миграции Alembic
echo "Running database migrations..."
uv run alembic upgrade head

echo "Migrations completed successfully"
echo "Starting bot..."

# Запускаем бота
exec uv run python -m src.main

