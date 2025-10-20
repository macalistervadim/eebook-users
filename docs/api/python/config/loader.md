# Загрузчик настроек

Модуль `loader` предоставляет функционал для безопасной загрузки настроек и секретов из защищенного хранилища в переменные окружения приложения. Использует паттерн "Провайдер секретов" для абстракции источника данных.

## Особенности

- Гибкая система загрузки секретов через абстрактный интерфейс `ISecretsProvider`
- Поддержка различных провайдеров секретов (по умолчанию используется Vault)
- Потокобезопасная работа с переменными окружения
- Детальное логирование операций
- Обработка ошибок с конкретными типами исключений

## Документация API

### SettingsLoader

::: src.config.loader.SettingsLoader
    options:
      show_source: true
      show_signature_annotations: true
      show_docstring: true
      show_bases: true
      show_root_heading: false
      show_root_toc_entry: false

## Примеры использования

### Базовое использование с Vault по умолчанию

```python
from src.config.loader import SettingsLoader

# Создание загрузчика с провайдером по умолчанию (Vault)
loader = SettingsLoader()

# Загрузка секретов в переменные окружения
await loader.load()

# Теперь секреты доступны через os.environ
import os
print(os.environ['DATABASE_URL'])  # Пример использования загруженного секрета
```

### Использование с кастомным провайдером

```python
from src.config.loader import SettingsLoader
from my_secrets_provider import MyCustomSecretsProvider

# Инициализация с пользовательским провайдером
custom_provider = MyCustomSecretsProvider()
loader = SettingsLoader(secrets_provider=custom_provider)

# Загрузка секретов
await loader.load()
```

## Рекомендации по использованию

1. **Инициализация**
   - Создавайте экземпляр `SettingsLoader` на ранних этапах инициализации приложения
   - Используйте внедрение зависимостей для передачи провайдера секретов

2. **Безопасность**
   - Никогда не храните реальные секреты в коде или системе контроля версий
   - Используйте минимально необходимые права доступа для токенов Vault
   - Регулярно обновляйте токены доступа

3. **Обработка ошибок**
   ```python
   try:
       loader = SettingsLoader()
       await loader.load()
   except SettingsLoaderInitializationError as e:
       # Обработка ошибок инициализации
       logger.error(f'Ошибка инициализации загрузчика: {e}')
       raise
   except Exception as e:
       # Обработка прочих ошибок
       logger.error(f'Неизвестная ошибка при загрузке настроек: {e}')
       raise
   ```

4. **Тестирование**
   - Используйте моки для `ISecretsProvider` в тестах
   - Тестируйте различные сценарии ошибок
   - Проверяйте корректность загрузки секретов в окружение


## Ограничения

- Поддерживается только асинхронный API
- По умолчанию загружаются только секреты из пути 'eebook/users'
- Все значения преобразуются в строки при загрузке в окружение
