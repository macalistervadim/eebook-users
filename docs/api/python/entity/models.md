# Модели сущностей

Модуль `entity.models` содержит Pydantic-схемы для работы с данными пользователей. Эти схемы обеспечивают валидацию, сериализацию и документирование данных на границах системы.

## Особенности

- Строгая типизация всех полей
- Встроенная валидация данных
- Сериализация/десериализация в JSON
- Поддержка документации OpenAPI
- Интеграция с FastAPI

## Документация API

### UserCreateSchema

Схема для создания нового пользователя.

::: src.entity.models.UserCreateSchema
    options:
      show_source: true
      show_signature_annotations: true
      show_docstring: true
      show_bases: true
      show_root_heading: false
      show_root_toc_entry: false

### UserResponseSchema

Схема для ответа с данными пользователя.

::: src.entity.models.UserResponseSchema
    options:
      show_source: true
      show_signature_annotations: true
      show_docstring: true
      show_bases: true
      show_root_heading: false
      show_root_toc_entry: false

### ChangePasswordSchema

Схема для смены пароля пользователя.

::: src.entity.models.ChangePasswordSchema
    options:
      show_source: true
      show_signature_annotations: true
      show_docstring: true
      show_bases: true
      show_root_heading: false
      show_root_toc_entry: false

## Примеры использования

### Создание пользователя

```python
from uuid import uuid4
from src.entity.models import UserCreateSchema, UserResponseSchema

# Валидация входящих данных
user_data = {
    "first_name": "Иван",
    "last_name": "Иванов",
    "email": "ivan@example.com",
    "username": "ivanov",
    "password": "secure_password123"
}

# Создание и валидация данных
user = UserCreateSchema(**user_data)

# Преобразование в формат ответа
response_data = UserResponseSchema(
    id=uuid4(),
    first_name=user.first_name,
    last_name=user.last_name,
    email=user.email,
    username=user.username,
    is_active=True,
    is_verified=False
)
```

### Смена пароля

```python
from src.entity.models import ChangePasswordSchema

# Валидация нового пароля
password_data = {"new_password": "new_secure_password123"}
change_password = ChangePasswordSchema(**password_data)
```

## Рекомендации по использованию

1. **Валидация данных**
   - Всегда используйте схемы для валидации входящих данных
   - Не передавайте сырые словари в бизнес-логику
   - Используйте встроенные валидаторы Pydantic

2. **Безопасность**
   - Никогда не возвращайте пароли в ответах API
   - Используйте разные схемы для ввода и вывода данных
   - Валидируйте входные данные как можно раньше

3. **Документирование**
   - Дополнительные поля документации можно добавить через `Field`
   - Используйте `example` и `description` для улучшения документации OpenAPI

## Интеграция с FastAPI

Схемы полностью совместимы с FastAPI и могут использоваться для:

- Валидации входных данных запросов
- Сериализации ответов API
- Генерации документации OpenAPI

## Ограничения

- Требуется Pydantic v2+
- Все поля должны быть явно типизированы
- Вложенные схемы должны быть определены до их использования
