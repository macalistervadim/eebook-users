import abc

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.model import User


class AbstractRepository(abc.ABC):
    """
    Абстрактный базовый класс для репозитория пользователей.

    Определяет интерфейс для работы с хранилищем пользователей,
    который должен быть реализован в конкретных классах-наследниках.
    """

    @abc.abstractmethod
    def add(self, user: User) -> None:
        """
        Добавляет пользователя в репозиторий.

        Args:
            user: Объект пользователя для добавления.

        Raises:
            NotImplementedError: Если метод не переопределен в подклассе.
        """
        raise NotImplementedError

    @abc.abstractmethod
    async def get_by_email(self, email: str) -> User | None:
        """
        Находит пользователя по email.

        Args:
            email: Email пользователя для поиска.

        Returns:
            User | None: Объект пользователя, если найден, иначе None.

        Raises:
            NotImplementedError: Если метод не переопределен в подклассе.
        """
        raise NotImplementedError


class SqlAlchemyRepository(AbstractRepository):
    """
    Реализация репозитория пользователей с использованием SQLAlchemy.

    Предоставляет методы для работы с хранилищем пользователей,
    используя асинхронную сессию SQLAlchemy.

    Args:
        session: Асинхронная сессия SQLAlchemy для работы с базой данных.
    """

    def __init__(self, session: AsyncSession) -> None:
        """
        Инициализирует репозиторий с указанной сессией SQLAlchemy.

        Args:
            session: Асинхронная сессия SQLAlchemy.
        """
        self.session = session

    def add(self, user: User) -> None:
        """
        Добавляет пользователя в сессию SQLAlchemy.

        Примечание:
            Изменения не сохраняются в базе данных до вызова session.commit().

        Args:
            user: Объект пользователя для добавления.
        """
        self.session.add(user)

    async def get_by_email(self, email: str) -> User | None:
        """
        Находит пользователя по email в базе данных.

        Args:
            email: Email пользователя для поиска.

        Returns:
            User | None: Объект пользователя, если найден, иначе None.

        Note:
            Выполняет асинхронный запрос к базе данных.
        """
        result = await self.session.execute(
            select(User).where(User.email == email),  # type: ignore
        )
        return result.scalars().first()
