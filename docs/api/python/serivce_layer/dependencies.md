# Service Layer Dependencies

Модуль `dependencies.py` содержит зависимости, используемые в сервисном слое приложения. Эти зависимости обеспечивают доступ к базовым сервисам, таким как база данных и настройки приложения.

## Основные зависимости

### `get_db() -> AsyncGenerator[AsyncSession, None]`
Асинхронный генератор, предоставляющий сессию базы данных.

**Особенности:**
- Создает новую сессию при каждом запросе
- Автоматически фиксирует изменения при успешном выполнении
- Откатывает транзакцию при возникновении ошибки
- Логирует ошибки базы данных

**Исключения:**
- `HTTPException(500)`: При ошибках работы с базой данных

### `get_settings() -> Settings`
Функция с кэшированием, возвращающая настройки приложения.

**Особенности:**
- Использует `lru_cache` для кэширования экземпляра настроек
- Возвращает экземпляр класса `Settings`
- Гарантирует единственный экземпляр настроек на всё приложение

## Пример использования

```python
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.service_layer.dependencies import get_db, get_settings

async def some_service(
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings)
):
    # Использование сессии базы данных
    result = await db.execute("SELECT 1")

    # Использование настроек
    debug_mode = settings.DEBUG

    return {"status": "ok"}
```

## Интеграция с FastAPI

Зависимости могут быть использованы в FastAPI следующим образом:

```python
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()

@router.get("/example")
async def example_route(
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings)
):
    # Логика обработки запроса
    pass
```

## Требования

- FastAPI с поддержкой внедрения зависимостей
- SQLAlchemy с поддержкой асинхронных сессий
- Настроенный экземпляр `Settings`

::: src.service_layer.dependencies
    options:
      heading_level: 2
      show_source: true
