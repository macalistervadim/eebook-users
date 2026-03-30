#!/bin/sh
set -e

APP_HOST="${APP_HOST:-0.0.0.0}"
APP_PORT="${APP_PORT:-8000}"

alembic upgrade head

exec uvicorn src.entrypoints.create_app:create_app_sync \
  --factory \
  --no-access-log \
  --host "$APP_HOST" \
  --port "$APP_PORT"
