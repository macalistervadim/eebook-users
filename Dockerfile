FROM python:3.13-alpine

RUN apk add --no-cache gcc musl-dev libffi-dev postgresql-dev curl

WORKDIR /app

COPY pyproject.toml uv.lock ./
COPY src ./src

RUN pip install --upgrade pip && pip install uv
RUN uv pip install --system --no-cache-dir -e .

COPY src /app/src
COPY tests /app/tests

CMD ["uv", "run", "uvicorn", "src.entrypoints.fastapi_app:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]
