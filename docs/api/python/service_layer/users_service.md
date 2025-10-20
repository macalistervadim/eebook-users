# Сервис пользователей

Модуль `users_service` предоставляет абстракции и реализации для работы с пользователями в сервисном слое приложения.

## Особенности

- Абстрактный базовый класс `ABCUserService` с полным набором методов для работы с пользователями
- Реализация `UserService` с бизнес-логикой работы с пользователями
- Интеграция с Unit of Work для управления транзакциями
- Поддержка хеширования паролей через абстракцию `IPasswordHasher`
- Полностью асинхронный API

## Документация API

### ABCUserService

Абстрактный базовый класс, определяющий интерфейс для работы с пользователями.

::: src.service_layer.users_service.ABCUserService
    options:
      show_source: true
      show_signature_annotations: true
      show_docstring: true
      show_bases: true
      show_root_heading: false
      show_root_toc_entry: false

### UserService

Реализация сервиса пользователей с бизнес-логикой.

::: src.service_layer.users_service.UserService
    options:
      show_source: true
      show_signature_annotations: true
      show_docstring: true
      show_bases: true
      show_root_heading: false
      show_root_toc_entry: false

## Примеры использования

### Регистрация нового пользователя

```python
# Создание экземпляра сервиса
uow = SqlAlchemyUnitOfWork(session_factory=session_factory, repo_factory=repo_factory)
hasher = BcryptPasswordHasher()
user_service = UserService(uow=uow, hasher=hasher)

# Регистрация пользователя
user = await user_service.register_user(
    first_name="Иван",
    last_name="Иванов",
    email="ivan@example.com",
    username="ivanov",
    password="securepassword123"
)
```

### Аутентификация пользователя

```python
# Аутентификация
is_authenticated = await user_service.login(
    email="ivan@example.com",
    password="securepassword123"
)

if is_authenticated:
    print("Аутентификация успешна")
else:
    print("Неверные учетные данные")
```

### Получение пользователя по ID

```python
user = await user_service.get_user_by_id(user_id=user_id)
if user:
    print(f"Найден пользователь: {user.email}")
```

## Лучшие практики

1. **Использование Unit of Work**: Все операции с базой данных выполняются в контексте Unit of Work, что обеспечивает атомарность операций.
2. **Валидация данных**: Входные данные должны быть валидированы до вызова методов сервиса.
3. **Обработка ошибок**: Методы могут вызывать исключения, которые должны быть обработаны на уровне API.
4. **Кэширование**: Для часто запрашиваемых данных рассмотрите возможность добавления кэширования.
5. **Асинхронность**: Все методы асинхронные и должны вызываться с использованием `await`.

## Интеграция

Модуль интегрируется с:

- FastAPI приложениями
- SQLAlchemy ORM через Unit of Work
- Системой аутентификации
- Системой хеширования паролей

## Ограничения

- Требует наличия настроенной базы данных
- Зависит от корректной работы Unit of Work
- Не поддерживает пакетные операции
- Нет встроенной поддержки пагинации для списков пользователей

## Дополнительные возможности

Модуль может быть расширен для поддержки:

- Восстановления пароля
- Двухфакторной аутентификации
- Управления ролями и разрешениями
- Аудит-лога операций с пользователями

## См. также

- [Документация по Unit of Work](./uow.md)
- [Документация по зависимостям](./dependencies.md)
- [Документация по модели пользователя](../domain/models.md)
