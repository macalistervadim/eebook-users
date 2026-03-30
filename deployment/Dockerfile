# syntax=docker/dockerfile:1

FROM python:3.13-slim AS base
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
WORKDIR /app

FROM base AS builder
RUN apt-get update && apt-get install -y --no-install-recommends build-essential libpq-dev curl \
    && rm -rf /var/lib/apt/lists/*
COPY pyproject.toml uv.lock ./
RUN pip install --upgrade pip && pip install uv
COPY src ./src
RUN uv pip install --system --no-cache-dir -e .

FROM base AS runtime
RUN apt-get update && apt-get install -y --no-install-recommends libpq-dev curl \
    && rm -rf /var/lib/apt/lists/* \
    && addgroup --system app && adduser --system --ingroup app app
COPY --from=builder /usr/local /usr/local
COPY src ./src
COPY alembic.ini ./alembic.ini
COPY deployment/entrypoints ./deployment/entrypoints
RUN mkdir -p /app/logs && chown -R app:app /app/logs
USER app
ENTRYPOINT ["/app/deployment/entrypoints/app.sh"]
