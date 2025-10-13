# Alembic Migrations
Модуль alembic используется для управления схемой базы данных — создания, изменения и версии таблиц.
Это официальный инструмент миграций для SQLAlchemy, позволяющий безопасно обновлять структуру БД без потери данных.

## Основные понятия
### Что такое миграции
Миграции — это набор версий схемы базы данных, которые позволяют:

- Создавать и изменять таблицы; 
- Добавлять и удалять столбцы; 
- Управлять внешними ключами и индексами; 
- Обновлять схему без необходимости пересоздавать базу данных.
Каждая миграция хранится как отдельный файл в директории `alembic/versions`.

## Основные компоненты Alembic
### 1. alembic.ini
Главный конфигурационный файл Alembic.

Содержит параметры подключения к базе данных и настройки путей.

Пример:
```
[alembic]
script_location = src/infrastructure/database/alembic

sqlalchemy.url = postgresql+asyncpg://user:password@localhost/eebook
```
### 2. env.py
Сценарий, который управляет применением миграций.

Здесь определяется, как Alembic подключается к базе данных (в том числе асинхронно).

Пример (для асинхронного варианта):

```python
from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context
from src.infrastructure.database.models import Base

config = context.config
fileConfig(config.config_file_name)
target_metadata = Base.metadata

async def run_migrations_online():
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

async def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()

import asyncio
asyncio.run(run_migrations_online())
```

---

# Основные команды
## Инициализация
Создать директорию миграций:
```
alembic init src/infrastructure/database/alembic
```

## Создание миграции
Сгенерировать новую миграцию на основе изменений моделей:
``` 
alembic revision --autogenerate -m "add users table"
```

## Автоматическое сравнение:
Alembic анализирует текущие модели (Base.metadata) и схему БД, формируя SQL-изменения.

## Применение миграций
Применить все новые миграции:
```
alembic upgrade head
```

Вернуться к предыдущей версии:
```
alembic downgrade -1
```

---

# Асинхронный вариант Alembic
Хотя Alembic изначально синхронный, его можно использовать с асинхронным SQLAlchemy при помощи async_engine_from_config.

Принцип:

- Alembic создаёт асинхронный движок;
- Внутри run_migrations_online используется await connection.run_sync();

Таким образом, миграции выполняются синхронно внутри асинхронного контекста.

!!! warning "Применение команд"
    Приведенные команды в данной статье могут отличаться от используемых напрямую в проекте в зависимости от используемой
    архитектуры и инструментария. Данные команды приведены для использования на "чистой" системе без использования инструментов
    по типу Vault, k8 и пр.
