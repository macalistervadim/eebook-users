# Фабрики репозиториев

Модуль `factory` содержит классы-фабрики для создания и настройки репозиториев пользователей. Основная цель - инкапсулировать логику создания репозиториев и их зависимостей, что упрощает управление жизненным циклом объектов и внедрение зависимостей.

## Документация API

::: src.adapters.factory
    options:
      show_root_heading: false
      show_source: true
      show_bases: true
      show_inheritance: true
      members:
        - ABCUsersRepositoryFactory
        - SQLAlchemyUsersRepositoryFactory
      show_root_toc_entry: false

## Пример использования

```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from src.adapters.factory import SQLAlchemyUsersRepositoryFactory
from src.adapters.hasher import BcryptPasswordHasher

# Инициализация зависимостей
hasher = BcryptPasswordHasher()
engine = create_async_engine("postgresql+asyncpg://user:password@localhost/db")

# Создание экземпляра репозитория
async with AsyncSession(engine) as session:
    factory = SQLAlchemyUsersRepositoryFactory(hasher=hasher)
    repository = factory.create(session=session)
    
    # Использование репозитория
    user = await repository.get_user_by_email("user@example.com")
```