# Модели данных приложения

Модуль `entity.models` содержит Pydantic-модели для валидации входящих данных. Эти модели используются для проверки и преобразования данных на границе API.

## Основные модели

### `RegisterModel`
Модель для валидации данных при регистрации нового пользователя.

**Поля:**
- `first_name: str` - имя пользователя
- `last_name: str` - фамилия пользователя
- `email: str` - электронная почта (должна быть валидным email-адресом)
- `password: str` - пароль пользователя

### `LoginModel`
Модель для валидации данных при аутентификации пользователя.

**Поля:**
- `email: str` - электронная почта пользователя
- `password: str` - пароль пользователя

## Примеры использования

### Регистрация пользователя
```python
from src.entity.models import RegisterModel

# Валидация и преобразование данных
user_data = {
    "first_name": "Иван",
    "last_name": "Иванов",
    "email": "ivan@example.com",
    "password": "secure_password123"
}

try:
    user = RegisterModel(**user_data)
    # Данные прошли валидацию
    print(f"Создан пользователь: {user.email}")
except ValueError as e:
    print(f"Ошибка валидации: {e}")
```

### Аутентификация пользователя
```python
from src.entity.models import LoginModel

# Валидация данных входа
login_data = {
    "email": "ivan@example.com",
    "password": "secure_password123"
}

try:
    credentials = LoginModel(**login_data)
    # Данные для входа корректны
    print(f"Попытка входа: {credentials.email}")
except ValueError as e:
    print(f"Ошибка валидации: {e}")
```

## Особенности

- **Валидация данных**: Автоматическая проверка типов и обязательных полей
- **Безопасность**: Пароли не обрабатываются и не хранятся в этой модели
- **Совместимость**: Легко интегрируется с FastAPI для валидации запросов

## Требования

- Требуется пакет `pydantic` для работы моделей

::: src.entity.models
    options:
      heading_level: 2
      show_source: true
