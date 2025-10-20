# Миграции базы данных

Модуль `migrations` предоставляет функционал для управления версионированием схемы базы данных с использованием Alembic.

## Особенности

- Поддержка асинхронных операций с базой данных
- Интеграция с настройками приложения
- Автоматическая генерация миграций
- Поддержка отката изменений
- Работа с Vault для получения секретов

## Документация API

### env.py


Основной скрипт конфигурации миграций Alembic.

::: src.infrastructure.database.migrations.env
    options:
      show_source: true
      show_signature_annotations: true
      show_docstring: true
      show_root_heading: false
      show_root_toc_entry: false

### init_settings_and_get_uri

Загружает настройки и возвращает URI для подключения к БД.

::: src.infrastructure.database.migrations.env.init_settings_and_get_uri
    options:
      show_source: true
      show_signature_annotations: true
      show_docstring: true
      show_root_heading: false
      show_root_toc_entry: false

## Примеры использования

### Создание новой миграции

```bash
alembic revision --autogenerate -m "Описание изменений"
```

### Применение миграций

```bash
# Применить все новые миграции
alembic upgrade head

# Откатить последнюю миграцию
alembic downgrade -1

# Применить конкретную миграцию
alembic upgrade <revision>
```

### Проверка текущей версии

```bash
alembic current
```

## Рекомендации по использованию

1. **Разработка**
   - Всегда добавляйте осмысленные сообщения к миграциям
   - Проверяйте сгенерированные миграции перед применением
   - Используйте `--autogenerate` с осторожностью
   - Храните миграции в системе контроля версий

2. **Безопасность**
   - Не включайте чувствительные данные в миграции
   - Используйте переменные окружения для конфиденциальной информации
   - Проверяйте SQL-запросы перед выполнением в production

3. **Производительность**
   - Для больших таблиц используйте `batch_alter_table`
   - Добавляйте индексы для часто используемых запросов
   - Избегайте блокирующих операций в транзакциях

## Интеграция

Модуль интегрируется с:

- SQLAlchemy ORM
- Alembic
- Vault для управления секретами
- Настройками приложения
- Системами логирования

## Ограничения

- Требуется Alembic 1.8+
- Зависит от синхронного драйвера БД для выполнения миграций
- Автоматическая генерация может потребовать ручной доработки

## Дополнительные возможности

### Кастомные шаблоны миграций

Шаблоны миграций можно настраивать через `script.py.mako`:

```python
"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}
"""
from alembic import op
import sqlalchemy as sa
${imports if imports else ""}

# revision identifiers, used by Alembic
revision = ${repr(up_revision)}
down_revision = ${repr(down_revision)}


def upgrade():
    ${upgrades if upgrades else "pass"}


def downgrade():
    ${downgrades if downgrades else "pass"}
```

### Обработка ошибок

```python
try:
    # Выполнение миграции
    context.run_migrations()
except Exception as e:
    logger.error(f"Ошибка при выполнении миграции: {e}")
    raise
```

### Расширенные сценарии

#### Миграция с обработкой данных

```python
def upgrade():
    # Создание новой таблицы
    op.create_table(
        'new_table',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('data', sa.String()),
        sa.PrimaryKeyConstraint('id')
    )

    # Копирование данных из старой таблицы
    connection = op.get_bind()
    connection.execute("""
        INSERT INTO new_table (id, data)
        SELECT id, old_data FROM old_table
    """)

    # Удаление старой таблицы
    op.drop_table('old_table')

    # Переименование новой таблицы
    op.rename_table('new_table', 'old_table')
```

#### Условное выполнение миграции

```python
def upgrade():
    inspector = inspect(engine)
    if 'old_table_name' in inspector.get_table_names():
        # Выполнить миграцию только если таблица существует
        op.drop_table('old_table_name')
```
