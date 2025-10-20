# Модуль хеширования паролей

Модуль `password_hasher` предоставляет реализацию интерфейса `IPasswordHasher` для безопасного хеширования и проверки паролей с использованием алгоритма Argon2.

## UserPasswordHasher

Реализация хешера паролей на основе Argon2. Argon2 — это победитель конкурса Password Hashing Competition 2015 года, обеспечивающий защиту от атак перебором и использованием специализированного оборудования.

### Особенности

- Использует современный и безопасный алгоритм Argon2
- Автоматически генерирует соль (salt) для каждого пароля
- Поддерживает настройку параметров вычислительной сложности
- Реализует интерфейс `IPasswordHasher`

### Детали реализации

::: src.adapters.password_hasher.UserPasswordHasher
    options:
      show_source: true
      show_signature_annotations: true

## Примеры использования
 Автоматически генерирует соль (salt) для каждого пароля
- Поддерживает настройку параметров вычислительной сложности
- Реализует интерфейс `IPasswordHasher`

### Детали реализации

::: src.adapters.password_hasher.UserPasswordHasher
    options:
      show_source: true
      show_signature_annotations: true

## Примеры использования

### Создание и использование хешера

```python
from src.adapters.password_hasher import UserPasswordHasher

# Создание экземпляра хешера
hasher = UserPasswordHasher()

# Хеширование пароля
hashed_password = hasher.hash_password("my_secure_password")

# Проверка пароля
is_valid = hasher.verify_password("my_secure_password", hashed_password)  # Вернет True
```

### Интеграция с пользовательской моделью

```python
from dataclasses import dataclass
from src.adapters.password_hasher import UserPasswordHasher

hasher = UserPasswordHasher()

@dataclass
class User:
    username: str
    _hashed_password: str
    
    def set_password(self, password: str) -> None:
        self._hashed_password = hasher.hash_password(password)
    
    def check_password(self, password: str) -> bool:
        return hasher.verify_password(password, self._hashed_password)
```

## Рекомендации

1. **Безопасность паролей**
   - Никогда не храните пароли в открытом виде
   - Используйте длинные и сложные пароли
   - Регулярно обновляйте параметры хеширования

2. **Производительность**
   - Настройте параметры сложности в соответствии с вашими требованиями
   - Учитывайте нагрузку на процессор при аутентификации большого числа пользователей

3. **Миграции**
   - При смене алгоритма хеширования предусмотрите механизм обновления хешей
   - Храните информацию о версии алгоритма хеширования

## Примечания

- Текущая реализация использует настройки по умолчанию библиотеки `passlib`
- Для продакшн-среды рекомендуется настроить параметры сложности в соответствии с вашими требованиями безопасности
