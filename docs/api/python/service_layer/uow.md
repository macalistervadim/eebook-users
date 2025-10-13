# Unit of Work (UoW) Pattern

Модуль `uow.py` реализует паттерн "Единица работы" (Unit of Work), который обеспечивает атомарность операций с базой данных и управление транзакциями.

## Основные компоненты

### `AbstractUnitOfWork`
Абстрактный базовый класс, определяющий интерфейс для работы с транзакциями.

**Методы:**
- `commit()` - фиксация изменений
- `rollback()` - откат изменений
- `__aenter__`/`__aexit__` - контекстный менеджер

### `SqlAlchemyUnitOfWork`
Конкретная реализация UoW для работы с SQLAlchemy.

**Особенности:**
- Управление сессиями базы данных
- Автоматический rollback при ошибках
- Интеграция с репозиториями

## Пример использования

```python
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from src.service_layer.uow import SqlAlchemyUnitOfWork

# Настройка подключения
engine = create_async_engine("postgresql+asyncpg://user:pass@localhost/db")
session_factory = async_sessionmaker(engine, expire_on_commit=False)

# Использование UoW
async with SqlAlchemyUnitOfWork(session_factory) as uow:
    # Работа с репозиториями
    user = await uow.users.get_by_id(1)
    user.name = "New Name"

    # Фиксация изменений
    await uow.commit()
```

## Преимущества

1. **Атомарность** - все изменения либо применяются, либо откатываются
2. **Изоляция** - каждая единица работы изолирована от других
3. **Управление ресурсами** - автоматическое освобождение ресурсов
4. **Гибкость** - легкая замена реализации при необходимости

## Требования

- SQLAlchemy с поддержкой асинхронности
- Настроенное подключение к базе данных

::: src.service_layer.uow
    options:
      heading_level: 2
      show_source: true
