# Интерфейсы адаптеров

Модуль `interfaces` содержит протоколы (контракты) для работы с внешними сервисами. Эти интерфейсы обеспечивают гибкость при интеграции с различными сервисами и упрощают тестирование.

## ISecretsProvider

Протокол для работы с хранилищами секретов. Определяет стандартный интерфейс для безопасного доступа к конфиденциальным данным.

### Когда использовать
- Для работы с различными хранилищами секретов (HashiCorp Vault, AWS Secrets Manager и т.д.)
- При необходимости изолировать логику работы с секретами от остального кода
- Для упрощения тестирования компонентов

### Детали реализации

::: src.adapters.interfaces.ISecretsProvider
    options:
      show_source: true
      show_signature_annotations: true

## IPasswordHasher

Протокол для безопасного хеширования и проверки паролей. Позволяет использовать различные алгоритмы хеширования.

### Особенности
- Поддержка различных алгоритмов хеширования
- Единая точка управления безопасностью паролей
- Простая интеграция с существующими системами аутентификации

### Детали реализации

::: src.adapters.interfaces.IPasswordHasher
    options:
      show_source: true
      show_signature_annotations: true

## Примеры использования

### Работа с ISecretsProvider

```python
from src.adapters.interfaces import ISecretsProvider

class VaultSecretsProvider(ISecretsProvider):
    async def get_secret(self, path: str, key: str | None = None) -> dict[str, Any]:
        # Реализация получения секрета
        ...
```

### Работа с IPasswordHasher

```python
from src.adapters.interfaces import IPasswordHasher

class BcryptPasswordHasher(IPasswordHasher):
    def verify_password(self, password: str, hashed_password: str) -> bool:
        # Проверка пароля
        ...
    
    def hash_password(self, password: str) -> str:
        # Хеширование пароля
        ...
```

## Рекомендации

1. Всегда внедряйте зависимости через конструктор
2. Создавайте мок-реализации для тестирования
3. Обрабатывайте ошибки на уровне реализации
4. Документируйте неочевидные аспекты реализации
