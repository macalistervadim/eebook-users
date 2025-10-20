# Движок базы данных

Модуль `engine` предоставляет функционал для работы с асинхронным подключением к базе данных с использованием SQLAlchemy.

## Особенности

- Ленивая инициализация движка БД
- Управление пулом соединений
- Обработка ошибок подключения
- Кэширование фабрики сессий
- Асинхронный API

## Документация API

### get_engine

Фабричная функция для создания и кэширования асинхронного движка SQLAlchemy.

::: src.infrastructure.database.engine.get_engine
    options:
      show_source: true
      show_signature_annotations: true
      show_docstring: true
      show_bases: true
      show_root_heading: false
      show_root_toc_entry: false

### get_session_factory

Фабрика для создания асинхронных сессий с настройками по умолчанию.

::: src.infrastructure.database.engine.get_session_factory
    options:
      show_source: true
      show_signature_annotations: true
      show_docstring: true
      show_bases: true
      show_root_heading: false
      show_root_toc_entry: false

## Примеры использования

### Получение движка и создание сессии

```python
from src.infrastructure.database.engine import get_engine, get_session_factory

# Получение движка (кэшируется при первом вызове)
engine = get_engine()

# Получение фабрики сессий (кэшируется при первом вызове)
session_factory = get_session_factory()

# Создание сессии
async with session_factory() as session:
    # Работа с базой данных
    result = await session.execute("SELECT 1")
    print(await result.scalar())
```

## Рекомендации по использованию

1. **Инициализация**
   - Убедитесь, что настройки приложения загружены до первого вызова `get_engine()`
   - Используйте `get_engine()` и `get_session_factory()` как фабричные функции
   - Не создавайте несколько экземпляров движка в одном приложении

2. **Настройки подключения**
   - Настройте параметры пула соединений в соответствии с нагрузкой
   - Используйте `pool_pre_ping` для обнаружения разорванных соединений
   - Установите разумные таймауты для окружения

3. **Обработка ошибок**
   - Обрабатывайте специфические исключения SQLAlchemy
   - Используйте контекстные менеджеры для управления сессиями
   - Логируйте ошибки подключения

## Интеграция

Модуль интегрируется с:
- SQLAlchemy ORM
- ASGI-приложениями
- Системами кэширования (через `lru_cache`)
- Системами логирования

## Ограничения

- Требуется SQLAlchemy 1.4+
- Зависит от асинхронного драйвера БД (например, asyncpg)
- Кэширование движка и фабрики сессий может быть нежелательным в тестовом окружении

## Дополнительные возможности

### Кастомные настройки движка

```python
from sqlalchemy.ext.asyncio import create_async_engine

def create_custom_engine(url: str) -> AsyncEngine:
    return create_async_engine(
        url,
        pool_size=10,
        max_overflow=20,
        pool_timeout=30,
        pool_pre_ping=True,
        pool_recycle=3600,
        connect_args={'command_timeout': 15},
    )
```

### Обработка ошибок подключения

```python
from src.infrastructure.database.exceptions import (
    DatabaseConnectionError,
    DatabaseTimeoutError,
    DatabaseArgumentError
)

try:
    engine = get_engine()
except DatabaseTimeoutError as e:
    # Обработка таймаута подключения
    logger.error(f"Таймаут подключения к БД: {e}")
    raise
```
