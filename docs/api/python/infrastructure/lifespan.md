# Управление жизненным циклом приложения

Модуль `lifespan` предоставляет функционал для управления жизненным циклом FastAPI приложения, обеспечивая корректную инициализацию и освобождение ресурсов.

## Особенности

- Асинхронное управление жизненным циклом
- Безопасная инициализация и освобождение ресурсов
- Интеграция с системой бутстраппинга
- Обработка ошибок при старте и завершении

## Документация API

### lifespan

Асинхронный контекстный менеджер для управления жизненным циклом приложения.

::: src.infrastructure.lifespan.lifespan
    options:
      show_source: true
      show_signature_annotations: true
      show_docstring: true
      show_bases: true
      show_root_heading: false
      show_root_toc_entry: false

## Примеры использования

### Базовое использование с FastAPI

```python
from fastapi import FastAPI
from src.infrastructure.lifespan import lifespan

# Создание приложения с кастомным жизненным циклом
app = FastAPI(lifespan=lifespan)

# Определение маршрутов...
@app.get("/")
async def root():
    return {"message": "Приложение работает"}
```

### Кастомизация жизненного цикла

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
from src.infrastructure.lifespan import lifespan as base_lifespan

@asynccontextmanager
async def custom_lifespan(app: FastAPI):
    # Дополнительная инициализация перед запуском
    print("Выполняется дополнительная инициализация...")
    
    # Использование базового жизненного цикла
    async with base_lifespan(app) as manager:
        # Код выполняется после инициализации приложения
        print("Приложение готово к работе")
        try:
            yield manager
        finally:
            # Дополнительная очистка при завершении
            print("Выполняется дополнительная очистка...")

app = FastAPI(lifespan=custom_lifespan)
```

## Рекомендации по использованию

1. **Инициализация ресурсов**
   - Используйте `bootstrap()` для централизованной инициализации
   - Инициализируйте только необходимые ресурсы
   - Обрабатывайте ошибки при инициализации

2. **Освобождение ресурсов**
   - Гарантируйте освобождение всех ресурсов в блоке `finally`
   - Используйте асинхронные менеджеры контекста
   - Обрабатывайте ошибки при освобождении ресурсов

3. **Логирование**
   - Логируйте ключевые этапы жизненного цикла
   - Включайте в логи информацию об ошибках
   - Используйте разные уровни логирования

## Интеграция

Модуль интегрируется с:

- FastAPI приложениями
- Системой бутстраппинга
- Движком базы данных
- Системой логирования

## Ограничения

- Требуется Python 3.8+
- Зависит от FastAPI с поддержкой lifespan
- Предполагает использование асинхронного кода

## Дополнительные возможности

### Добавление хуков жизненного цикла

```python
from fastapi import FastAPI
from src.infrastructure.lifespan import lifespan as base_lifespan

app = FastAPI()

# Добавление обработчиков событий жизненного цикла
@app.on_event("startup")
async def startup_event():
    print("Дополнительная инициализация при запуске")

@app.on_event("shutdown")
async def shutdown_event():
    print("Дополнительная очистка при завершении")

# Использование базового жизненного цикла
app.router.lifespan_context = base_lifespan
```

### Обработка ошибок при инициализации

```python
from fastapi import FastAPI, HTTPException
from src.infrastructure.lifespan import lifespan as base_lifespan

@asynccontextmanager
async def safe_lifespan(app: FastAPI):
    try:
        async with base_lifespan(app):
            yield
    except Exception as e:
        # Логирование критической ошибки
        print(f"Критическая ошибка при инициализации: {e}")
        
        # Генерация понятной ошибки для пользователя
        @app.get("/")
        async def error_route():
            raise HTTPException(
                status_code=503,
                detail="Сервис временно недоступен из-за ошибки инициализации"
            )
        
        # Позволяет приложению запуститься в деградированном режиме
        yield

app = FastAPI(lifespan=safe_lifespan)
```
