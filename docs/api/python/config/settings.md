# Настройки приложения

Модуль `settings` предоставляет централизованное управление конфигурацией приложения с использованием Pydantic. Это обеспечивает строгую типизацию и валидацию настроек.

## Основные возможности

- Типизированное хранение настроек
- Автоматическая загрузка из переменных окружения
- Генерация URI для подключения к БД
- Поддержка дополнительных настроек через `extra = 'allow'`

## Класс `Settings`

Основной класс, наследующийся от `pydantic.BaseSettings`. Содержит все настройки приложения.

### Обязательные параметры

- `FASTAPI_SECRET`: Секретный ключ для FastAPI
- `POSTGRES_USER`: Имя пользователя PostgreSQL
- `POSTGRES_PASSWORD`: Пароль пользователя PostgreSQL
- `POSTGRES_DB`: Имя базы данных
- `POSTGRES_PORT`: Порт PostgreSQL
- `POSTGRES_HOST`: Хост PostgreSQL
- и др

### Вычисляемые свойства

- `postgres_uri`: Формирует строку подключения к PostgreSQL в формате:
  ```
  postgresql+asyncpg://{user}:{password}@{host}:{port}/{dbname}
  ```

## Пример использования

```python
from src.config.settings import Settings

# Автоматически загружает настройки из переменных окружения
settings = Settings()

# Использование настроек
db_uri = settings.postgres_uri
secret = settings.FASTAPI_SECRET
```

## Настройка окружения

1. Создайте файл `.env` в корне проекта:
   ```env
   FASTAPI_SECRET=your_secret_key
   POSTGRES_USER=postgres
   POSTGRES_PASSWORD=your_password
   POSTGRES_DB=your_database
   POSTGRES_PORT=5432
   POSTGRES_HOST=localhost
   ```

2. Установите переменные окружения в системе

## Валидация

Pydantic автоматически проверяет типы и обязательность полей при создании экземпляра `Settings`.

## Дополнительные настройки

Класс настроен на чтение из файла `.env` с кодировкой UTF-8 и разрешает дополнительные поля через `extra = 'allow'`.

::: src.config.settings.Settings
    options:
      heading_level: 3
      show_source: true
      show_signature: false
