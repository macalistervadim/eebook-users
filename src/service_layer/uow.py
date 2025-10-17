import abc

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
)

from src.adapters.repository import (
    ABCUsersRepository,
    ABCUsersRepositoryFactory,
)


class AbstractUnitOfWork(abc.ABC):
    """Абстрактный базовый класс Unit of Work (Единица работы).

    Предоставляет интерфейс для управления транзакциями и доступа к репозиториям.

    Атрибуты:
        users: Репозиторий для работы с пользователями.
    """

    users: ABCUsersRepository

    async def __aenter__(self) -> 'AbstractUnitOfWork':
        """Вход в контекстный менеджер.

        Returns:
            AbstractUnitOfWork: Текущий экземпляр Unit of Work.

        """
        return self

    async def __aexit__(self, *args) -> None:
        """Выход из контекстного менеджера с откатом несохраненных изменений.

        Args:
            *args: Аргументы исключения, если оно произошло в блоке with.

        """
        await self.rollback()

    async def commit(self) -> None:
        """Фиксирует все изменения в рамках текущей единицы работы.

        Raises:
            Exception: Если произошла ошибка при фиксации изменений.

        """
        await self._commit()

    @abc.abstractmethod
    async def _commit(self) -> None:
        """Абстрактный метод для реализации фиксации изменений.

        Должен быть переопределен в подклассах для конкретной реализации.

        Raises:
            NotImplementedError: Если метод не переопределен в подклассе.

        """
        raise NotImplementedError

    @abc.abstractmethod
    async def rollback(self) -> None:
        """Абстрактный метод для отката изменений.

        Должен быть переопределен в подклассах для конкретной реализации.

        Raises:
            NotImplementedError: Если метод не переопределен в подклассе.

        """
        raise NotImplementedError


class SqlAlchemyUnitOfWork(AbstractUnitOfWork):
    """Unit of Work для работы с SQLAlchemy.

    Обеспечивает управление сессиями базы данных и транзакциями
    с использованием SQLAlchemy.
    """

    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        repo_factory: ABCUsersRepositoryFactory,
    ):
        """Инициализация SqlAlchemyUnitOfWork.

        Args:
            session_factory: Фабрика для создания асинхронных сессий SQLAlchemy.
            repo_factory: Фадрика создания репозитория для работы с данными

        """
        self.session_factory = session_factory
        self.repo_factory = repo_factory

    async def __aenter__(self):
        """Вход в контекстный менеджер.

        Инициализирует сессию базы данных и репозитории.

        Returns:
            SqlAlchemyUnitOfWork: Текущий экземпляр Unit of Work.

        """
        self.session: AsyncSession = self.session_factory()
        self.users = self.repo_factory.create(self.session)
        return await super().__aenter__()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Выход из контекстного менеджера.

        При возникновении исключения выполняет откат изменений,
        иначе фиксирует изменения. В любом случае закрывает сессию.

        Args:
            exc_type: Тип исключения, если оно произошло, иначе None.
            exc_val: Экземпляр исключения, если оно произошло, иначе None.
            exc_tb: Трассировка стека, если исключение произошло, иначе None.

        Returns:
            bool: Результат выполнения родительского метода __aexit__.

        """
        if exc_type:
            await self.rollback()
        else:
            await self._commit()
        await self.session.close()
        return await super().__aexit__(exc_type, exc_val, exc_tb)

    async def _commit(self):
        """Фиксирует изменения в базе данных.

        Raises:
            SQLAlchemyError: Если произошла ошибка при фиксации транзакции.

        """
        await self.session.commit()

    async def rollback(self):
        """Выполняет откат текущей транзакции.

        Отменяет все изменения, сделанные в рамках текущей сессии.
        """
        await self.session.rollback()
