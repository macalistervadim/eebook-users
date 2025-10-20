# Модуль репозитория пользователей

Модуль `repository` реализует паттерн Repository для работы с данными пользователей. Содержит абстрактный базовый класс и его реализацию на SQLAlchemy.

## ABCUsersRepository

Абстрактный базовый класс, определяющий интерфейс для работы с хранилищем пользователей.

### Документация API

::: src.adapters.repository.ABCUsersRepository
    options:
      show_source: true
      show_signature_annotations: true
      show_docstring: true
      show_bases: true
      show_root_heading: false
      show_root_toc_entry: false

## SQLAlchemyUsersRepository

Реализация репозитория пользователей на базе SQLAlchemy с асинхронной поддержкой.

### Особенности

- Полностью асинхронная работа с базой данных
- Поддержка Unit of Work (UoW)
- Автоматическое преобразование между ORM-моделями и доменными объектами
- Встроенная валидация данных

### Документация API

::: src.adapters.repository.SQLAlchemyUsersRepository
    options:
      show_source: true
      show_signature_annotations: true
      show_docstring: true
      show_bases: true
      show_root_heading: false
      show_root_toc_entry: false

## Примеры использования

### Создание репозитория

```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from src.adapters.repository import SQLAlchemyUsersRepository
from src.adapters.hasher import BcryptPasswordHasher

# Инициализация зависимостей
engine = create_async_engine("postgresql+asyncpg://user:password@localhost/db")
hasher = BcryptPasswordHasher()

# Создание сессии и репозитория
async with AsyncSession(engine) as session:
    repo = SQLAlchemyUsersRepository(session, hasher)
    
    # Использование репозитория
    user = await repo.get_by_email("user@example.com")
```

### Работа с пользователями

```python
# Добавление пользователя
new_user = User(
    email="new@example.com",
    hashed_password="secure_password",
    is_active=True
)
await repo.add(new_user)

# Поиск пользователя
user = await repo.get_by_email("new@example.com")

# Обновление данных
user.first_name = "Иван"
await repo.update(user)

# Удаление пользователя
await repo.remove(user.id)
```

## Рекомендации

1. **Управление сессиями**
   - Всегда используйте контекстный менеджер `async with` для работы с сессиями
   - Не храните ссылки на сессии дольше необходимого

2. **Обработка ошибок**
   - Обрабатывайте специфические исключения SQLAlchemy
   - Используйте транзакции для группировки операций

3. **Производительность**
   - Используйте `selectinload` для загрузки связанных сущностей
   - Применяйте пагинацию для больших выборок

4. **Тестирование**
   - Используйте тестовую базу данных
   - Применяйте фикстуры для подготовки тестовых данных
   - Проверяйте изоляцию тестов
