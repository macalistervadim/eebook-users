# Руководство по устранению неполадок при запуске проекта

В этом руководстве собраны наиболее распространённые проблемы, с которыми вы можете столкнуться при запуске проекта, и способы их решения.

## Содержание
- [Проблемы с базой данных](#проблемы-с-базой-данных)

## Проблемы с базой данных

### 1. Ошибка инициализации PostgreSQL в Docker
**Симптомы**:
```
postgres-1 | Error: Database is uninitialized and superuser password is not specified.
```

**Причина**:
При инициализации приложения в Docker-контейнере переменные окружения из Vault ещё не загружены, поэтому Docker не может получить необходимые данные для инициализации PostgreSQL.

**Решение**:
1. Добавьте в `docker-compose.yml` для сервиса PostgreSQL явное указание переменных окружения:
   ```yaml
   services:
     postgres:
       image: postgres:13
       environment:
         POSTGRES_USER: your_username
         POSTGRES_PASSWORD: your_secure_password
         POSTGRES_DB: your_database_name
       volumes:
         - postgres_data:/var/lib/postgresql/data
   
   volumes:
     postgres_data:
   ```

2. Пересоберите и перезапустите контейнеры:
   ```bash
   docker-compose down -v
   make up
   ```

## Получение дополнительной помощи

Если вы не нашли решение своей проблемы в этом руководстве, попробуйте:

1. Проверить [Issues](https://github.com/macalistervadim/eebook-users/issues) на GitHub
2. Создать новый Issue с описанием проблемы
3. Указать версии используемого ПО
4. Приложить логи ошибок
5. Описать шаги для воспроизведения проблемы
