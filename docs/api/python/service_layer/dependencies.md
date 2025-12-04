# Зависимости сервисного слоя

Модуль `dependencies` предоставляет фабрики и провайдеры зависимостей для сервисного слоя приложения, используя паттерн внедрения зависимостей.

## Особенности

- Кэширование часто используемых зависимостей
- Асинхронная загрузка зависимостей
- Поддержка единицы работы (Unit of Work)
- Интеграция с репозиториями и сервисами
- Управление жизненным циклом зависимостей

## Документация API

### get_settings

Фабрика для получения настроек приложения с кэшированием.

::: src.service_layer.dependencies.get_settings
    options:
      show_source: true
      show_signature_annotations: true
      show_docstring: true
      show_root_heading: false
      show_root_toc_entry: false

### get_uow

Провайдер для единицы работы (Unit of Work).

::: src.service_layer.dependencies.get_uow
    options:
      show_source: true
      show_signature_annotations: true
      show_docstring: true
      show_root_heading: false
      show_root_toc_entry: false

### get_repo_factory

Фабрика для создания репозиториев.

::: src.service_layer.dependencies.get_repo_factory
    options:
      show_source: true
      show_signature_annotations: true
      show_docstring: true
      show_root_heading: false
      show_root_toc_entry: false

### get_hasher

Провайдер для сервиса хеширования паролей.

::: src.service_layer.dependencies.get_hasher
    options:
      show_source: true
      show_signature_annotations: true
      show_docstring: true
      show_root_heading: false
      show_root_toc_entry: false

### get_user_service

Фабрика для сервиса работы с пользователями.

::: src.service_layer.dependencies.get_user_service
    options:
      show_source: true
      show_signature_annotations: true
      show_docstring: true
      show_root_heading: false
      show_root_toc_entry: false

## Примеры использования

### Базовое использование в FastAPI

```python
from fastapi import APIRouter, Depends
from src.service_layer.dependencies import get_user_service
from src.service_layer.users_service import UserService

router = APIRouter()

@router.get("/users/{user_id}")
async def get_user(
    user_id: int,
    user_service: UserService = Depends(get_user_service)
):
    user = await user_service.get_user(user_id)
    return {"user": user}
```

### Кастомизация зависимостей

```python
from functools import lru_cache
from src.service_layer.dependencies import get_hasher
from src.config.settings import get_settings
from src.adapters.factory import CustomUsersRepositoryFactory


# Переопределение фабрики репозиториев
async def get_custom_repo_factory():
    hasher = await get_hasher()
    return CustomUsersRepositoryFactory(hasher)


# Использование кастомной фабрики
@lru_cache
def get_custom_settings():
    settings = get_settings()
    # Модификация настроек
    settings.DEBUG = True
    return settings
```

## Рекомендации по использованию

1. **Управление зависимостями**
   - Используйте `lru_cache` для дорогих в создании зависимостей
   - Разделяйте зависимости по уровням абстракции
   - Избегайте циклических импортов

2. **Тестирование**
   - Заменяйте зависимости на моки в тестах
   - Используйте фикстуры для настройки тестового окружения
   - Изолируйте тесты друг от друга

3. **Производительность**
   - Кэшируйте тяжелые зависимости
   - Используйте ленивую загрузку, где это возможно
   - Избегайте блокирующих операций при инициализации

## Интеграция

Модуль интегрируется с:

- FastAPI приложениями
- SQLAlchemy ORM
- Системой аутентификации
- Сервисным слоем приложения
- Репозиториями доступа к данным

## Ограничения

- Требуется Python 3.8+
- Зависит от FastAPI и SQLAlchemy
- Предполагает использование асинхронного кода

## Дополнительные возможности

### Создание кастомных провайдеров

```python
from typing import Any
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

async def get_db_session() -> AsyncSession:
    """Провайдер сессии БД с автоматическим управлением жизненным циклом."""
    session_factory = get_session_factory()
    async with session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise

# Использование в зависимостях
async def get_user_service(
    session: AsyncSession = Depends(get_db_session)
) -> UserService:
    return UserService(session=session)
```

### Кэширование зависимостей

```python
from functools import lru_cache
from src.config.settings import get_settings


@lru_cache
def get_cached_service():
    """Пример кэширования сервиса с настройками."""
    settings = get_settings()
    return SomeService(settings)


# Использование в FastAPI маршруте
@router.get("/some-route")
async def some_route(
        service: SomeService = Depends(get_cached_service)
):
    result = await service.do_something()
    return {"result": result}
```
