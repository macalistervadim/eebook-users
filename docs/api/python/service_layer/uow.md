# Unit of Work (Единица работы)

Модуль `uow` реализует паттерн "Unit of Work" для управления транзакциями и доступа к репозиториям в сервисном слое приложения.

## Особенности

- Абстракция для управления транзакциями
- Поддержка асинхронных операций
- Интеграция с SQLAlchemy
- Автоматическое управление жизненным циклом сессии
- Поддержка отката изменений

## Документация API

### AbstractUnitOfWork

Абстрактный базовый класс для реализации паттерна Unit of Work.

::: src.service_layer.uow.AbstractUnitOfWork
    options:
      show_source: true
      show_signature_annotations: true
      show_docstring: true
      show_root_heading: false
      show_root_toc_entry: false

### SqlAlchemyUnitOfWork

Реализация Unit of Work для работы с SQLAlchemy.

::: src.service_layer.uow.SqlAlchemyUnitOfWork
    options:
      show_source: true
      show_signature_annotations: true
      show_docstring: true
      show_root_heading: false
      show_root_toc_entry: false

## Примеры использования

### Базовое использование

```python
from sqlalchemy.ext.asyncio import async_sessionmaker
from src.service_layer.uow import SqlAlchemyUnitOfWork
from src.adapters.factory import SQLAlchemyUsersRepositoryFactory

# Инициализация фабрики сессий и репозиториев
session_factory = async_sessionmaker(engine, expire_on_commit=False)
repo_factory = SQLAlchemyUsersRepositoryFactory(hasher)

# Использование Unit of Work
async with SqlAlchemyUnitOfWork(session_factory, repo_factory) as uow:
    # Работа с пользователями через репозиторий
    user = await uow.users.get_by_email("user@example.com")
    user.update_last_login()
    
    # Фиксация изменений
    await uow.commit()
```

### Обработка ошибок

```python
from sqlalchemy import exc

try:
    async with SqlAlchemyUnitOfWork(session_factory, repo_factory) as uow:
        user = await uow.users.get_by_id(1)
        user.balance -= amount
        await uow.commit()
except exc.SQLAlchemyError as e:
    logger.error(f"Ошибка при обновлении баланса: {e}")
    raise
```

## Рекомендации по использованию

1. **Управление транзакциями**
   - Всегда используйте `commit()` для сохранения изменений
   - Обрабатывайте исключения и используйте `rollback()` при ошибках
   - Избегайте вложенных блоков Unit of Work

2. **Работа с репозиториями**
   - Получайте доступ к репозиториям через атрибуты UoW
   - Не сохраняйте ссылки на репозитории вне контекста UoW
   - Используйте фабрики репозиториев для создания экземпляров

3. **Производительность**
   - Минимизируйте время удержания сессии
   - Используйте `expire_on_commit=False` для предотвращения лишних запросов
   - Избегайте N+1 запросов при загрузке связанных сущностей

## Интеграция

Модуль интегрируется с:

- SQLAlchemy ORM
- Асинхронными сессиями SQLAlchemy
- Репозиториями доступа к данным
- Сервисным слоем приложения
- Системой логирования

## Ограничения

- Требуется Python 3.8+
- Зависит от SQLAlchemy с поддержкой асинхронности
- Предполагает использование контекстных менеджеров

## Дополнительные возможности

### Кастомная реализация Unit of Work

```python
from typing import Any
from contextlib import asynccontextmanager

class CustomUnitOfWork(AbstractUnitOfWork):
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self.connection = None
        self.transaction = None
        self.users = CustomUsersRepository()

    async def __aenter__(self):
        self.connection = await create_connection(self.connection_string)
        self.transaction = self.connection.begin()
        return self

    async def _commit(self):
        await self.transaction.commit()

    async def rollback(self):
        if self.transaction:
            await self.transaction.rollback()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            await self.rollback()
        if self.connection:
            await self.connection.close()
```

### Использование с FastAPI

```python
from fastapi import Depends
from sqlalchemy.ext.asyncio import async_sessionmaker
from src.service_layer.uow import SqlAlchemyUnitOfWork

async def get_uow() -> SqlAlchemyUnitOfWork:
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    repo_factory = SQLAlchemyUsersRepositoryFactory(hasher)
    return SqlAlchemyUnitOfWork(session_factory, repo_factory)

@router.post("/users/{user_id}/update")
async def update_user(
    user_id: int,
    data: UserUpdate,
    uow: SqlAlchemyUnitOfWork = Depends(get_uow)
):
    async with uow:
        user = await uow.users.get_by_id(user_id)
        user.update(**data.dict())
        await uow.commit()
        return {"status": "success"}
```
