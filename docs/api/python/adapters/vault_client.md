# Vault Client

Модуль `vault` предоставляет клиент для безопасной работы с HashiCorp Vault - системой для хранения и управления секретами. Основной класс `VaultClient` инкапсулирует всю логику взаимодействия с Vault API, включая аутентификацию и чтение секретов.

## Особенности

- Поддержка аутентификации с помощью токена
- Автоматическая обработка KV Secrets Engine v2
- Полностью асинхронный API
- Расширенная обработка ошибок с конкретными типами исключений
- Логирование всех операций

## Документация API

### VaultClient

::: src.adapters.vault.VaultClient
    options:
      show_source: true
      show_signature_annotations: true
      show_docstring: true
      show_bases: true
      show_root_heading: false
      show_root_toc_entry: false

## Примеры использования

### Инициализация клиента

```python
from src.adapters.vault import VaultClient

# Инициализация с явным указанием параметров
vault = VaultClient(
    addr='http://localhost:8200',  # Адрес сервера Vault
    token_file='/path/to/vault/token'  # Файл с токеном доступа
)

# Или с использованием переменных окружения
# export VAULT_ADDR='http://localhost:8200'
# export VAULT_TOKEN_FILE='/path/to/vault/token'
vault = VaultClient()
```

### Работа с секретами

```python
# Чтение всего секрета
secret = await vault.get_secret('eebook/database')
# Результат: {'username': 'admin', 'password': 's3cr3t'}

# Чтение конкретного ключа из секрета
db_password = await vault.get_secret('eebook/database', key='password')
# Результат: 's3cr3t'

# Обработка ошибок
try:
    secret = await vault.get_secret('nonexistent/secret')
except VaultSecretNotFoundError:
    print('Секрет не найден')
except VaultPermissionError:
    print('Недостаточно прав для доступа к секрету')
except VaultError as e:
    print(f'Ошибка Vault: {e}')
```

## Рекомендации по использованию

1. **Безопасность**
   - Никогда не храните токены в коде или системе контроля версий
   - Используйте минимально необходимые права доступа для токенов
   - Регулярно обновляйте токены доступа

2. **Обработка ошибок**
   - Всегда обрабатывайте специфические исключения Vault
   - Реализуйте механизм повторных попыток при временных сбоях
   - Логируйте ошибки для последующего аудита

3. **Производительность**
   - Кэшируйте часто используемые секреты на стороне приложения
   - Избегайте частых обращений к Vault за одними и теми же данными
   - Используйте пулы соединений для часто используемых клиентов

4. **Тестирование**
   - Используйте моки для тестирования без реального сервера Vault
   - Тестируйте различные сценарии ошибок
   - Проверяйте обработку отсутствующих или невалидных данных

## Обработка ошибок

Модуль определяет несколько типов исключений для различных сценариев сбоев:

- `VaultError`: Базовый класс для всех исключений Vault
- `VaultConnectionError`: Ошибка подключения к серверу Vault
- `VaultTokenError`: Ошибка аутентификации или невалидный токен
- `VaultPermissionError`: Недостаточно прав для выполнения операции
- `VaultSecretNotFoundError`: Запрашиваемый секрет не найден

## Переменные окружения

- `VAULT_ADDR`: URL сервера Vault (например, 'http://localhost:8200')
- `VAULT_TOKEN_FILE`: Путь к файлу, содержащему токен аутентификации
