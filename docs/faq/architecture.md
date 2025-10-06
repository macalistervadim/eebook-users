# Архитектура проекта и принципы

Проект **eebook** построен с учётом **Domain-Driven Design (DDD)** и **Clean Architecture**.

## Основные слои

1. **Domain Layer**
   - Содержит бизнес-логику и модели: `domain/`, `entity/`
   - Примеры: `Portfolio`, `Asset`, `Transaction`
   - Абстракции не зависят от базы данных и фреймворков

2. **Service Layer**
   - Координирует работу domain-моделей
   - Реализует бизнес-процессы: пересчёт доходности, расчёт метрик

3. **Adapters / Infrastructure Layer**
   - Работа с внешними системами (DB, Vault, API)
   - Примеры: `adapters/vault.py`, `adapters/repository.py`
   - Изоляция внешних зависимостей через интерфейсы

4. **Entry Points / API Layer**
   - FastAPI приложения и эндпоинты
   - Взаимодействие с пользователем и внешним миром

---

## Принципы проектирования

- **Separation of Concerns (SoC)** — каждый слой отвечает за своё
- **Dependency Inversion Principle (DIP)** — зависимости направлены внутрь, слои high-level не зависят от low-level
- **DRY (Don't Repeat Yourself)** — минимизация дублирования кода
- **KISS (Keep It Simple, Stupid)** — код простой и читаемый
- **YAGNI (You Aren't Gonna Need It)** — не добавляем функционал без нужды
- **Unit of Work** и **Repository Pattern** для работы с БД
- **Immutable Data Objects** там, где это возможно

---

## Структура каталогов
```
src/
   ├─ adapters/ # инфраструктура (DB, Vault, внешние API)
   ├─ domain/ # бизнес-логика и модели
   ├─ entity/ # сущности проекта (Portfolio, Asset, Transaction)
   ├─ service_layer/ # бизнес-сервисы, координация логики
   ├─ entrypoints/ # FastAPI endpoints
```


---

## Важные соглашения

- Все публичные методы должны иметь докстринги
- Слой domain не должен зависеть от adapters
- Любая работа с БД/внешним API через интерфейсы
- Тестируем бизнес-логику независимо от инфраструктуры
