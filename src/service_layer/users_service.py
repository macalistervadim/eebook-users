import abc
import uuid

from src.adapters.interfaces import IPasswordHasher
from src.domain.model import User
from src.service_layer.uow import AbstractUnitOfWork


class ABCUserService(abc.ABC):
    """Абстрактный базовый класс сервиса пользователей.

    Определяет интерфейс для работы с пользователями,
    который должен быть реализован в конкретных классах-наследниках.
    """

    @abc.abstractmethod
    async def register_user(
        self,
        first_name: str,
        last_name: str,
        email: str,
        username: str,
        password: str,
    ) -> User:
        """Создаёт нового пользователя и сохраняет его в репозиторий.

        Args:
            first_name: Имя пользователя.
            last_name: Фамилия пользователя.
            email: Email пользователя.
            username: Логин пользователя.
            password: Пароль пользователя.

        Returns:
            User: Созданный объект пользователя.

        Raises:
            NotImplementedError: Если метод не переопределён в подклассе.

        """
        raise NotImplementedError

    @abc.abstractmethod
    async def login(self, email: str, password: str) -> bool:
        """Проверяет логин пользователя и обновляет время последнего входа.

        Args:
            email: Email пользователя.
            password: Пароль пользователя.

        Returns:
            bool: True, если аутентификация успешна, иначе False.

        Raises:
            NotImplementedError: Если метод не переопределён в подклассе.

        """
        raise NotImplementedError

    @abc.abstractmethod
    async def change_password(self, user_id: uuid.UUID, new_password: str) -> None:
        """Меняет пароль пользователя.

        Args:
            user_id: ID пользователя.
            new_password: Новый пароль.

        Raises:
            ValueError: Если пользователь с указанным ID не найден.
            NotImplementedError: Если метод не переопределён в подклассе.

        """
        raise NotImplementedError

    @abc.abstractmethod
    async def activate_user(self, user_id: uuid.UUID) -> None:
        """Активирует пользователя.

        Args:
            user_id: ID пользователя.

        Raises:
            NotImplementedError: Если метод не переопределён в подклассе.

        """
        raise NotImplementedError

    @abc.abstractmethod
    async def deactivate_user(self, user_id: uuid.UUID) -> None:
        """Деактивирует пользователя.

        Args:
            user_id: ID пользователя.

        Raises:
            NotImplementedError: Если метод не переопределён в подклассе.

        """
        raise NotImplementedError

    @abc.abstractmethod
    async def verify_email(self, user_id: uuid.UUID) -> None:
        """Подтверждает email пользователя.

        Args:
            user_id: ID пользователя.

        Raises:
            NotImplementedError: Если метод не переопределён в подклассе.

        """
        raise NotImplementedError

    @abc.abstractmethod
    async def get_user_by_email(self, email: str) -> User | None:
        """Находит пользователя по email.

        Args:
            email: Email пользователя.

        Returns:
            User | None: Найденный объект пользователя или None.

        Raises:
            NotImplementedError: Если метод не переопределён в подклассе.

        """
        raise NotImplementedError

    @abc.abstractmethod
    async def get_user_by_id(self, user_id: uuid.UUID) -> User | None:
        """Находит пользователя по ID.

        Args:
            user_id: ID пользователя.

        Returns:
            User | None: Найденный объект пользователя или None.

        Raises:
            NotImplementedError: Если метод не переопределён в подклассе.

        """
        raise NotImplementedError

    @abc.abstractmethod
    async def get_user_by_username(self, username: str) -> User | None:
        """Находит пользователя по username.

        Args:
            username: Логин пользователя.

        Returns:
            User | None: Найденный объект пользователя или None.

        Raises:
            NotImplementedError: Если метод не переопределён в подклассе.

        """
        raise NotImplementedError

    @abc.abstractmethod
    async def list_users(self, only_active: bool = False) -> list[User]:
        """Возвращает список пользователей.

        Args:
            only_active: Если True, возвращает только активных пользователей.

        Returns:
            list[User]: Список пользователей.

        Raises:
            NotImplementedError: Если метод не переопределён в подклассе.

        """
        raise NotImplementedError


class UserService(ABCUserService):
    """Сервисный слой для работы с пользователями (бизнес-логика)."""

    def __init__(self, uow: AbstractUnitOfWork, hasher: IPasswordHasher) -> None:
        """Инициализация сервиса.

        Args:
            uow: Unit of Work для управления транзакциями и репозиториями.
            hasher: Сервис для хеширования и проверки паролей.

        """
        self.uow = uow
        self.hasher = hasher

    async def register_user(
        self,
        first_name: str,
        last_name: str,
        email: str,
        username: str,
        password: str,
    ) -> User:
        hashed = self.hasher.hash_password(password)
        user = User(
            user_id=None,
            first_name=first_name,
            last_name=last_name,
            email=email,
            username=username,
            hashed_password=hashed,
            _hasher=self.hasher,
        )

        async with self.uow as uow:
            await uow.users.add(user)
            await uow.commit()
        return user

    async def remove_user(self, user_id: uuid.UUID) -> None:
        """Удаляет пользователя по ID.

        Args:
            user_id: ID пользователя.

        Raises:
            Exception: Если произошла ошибка при удалении пользователя.

        """
        async with self.uow as uow:
            await uow.users.remove(user_id)
            await uow.commit()

    async def login(self, email: str, password: str) -> bool:
        async with self.uow as uow:
            user = await uow.users.get_by_email(email)
            if not user:
                return False
            if not self.hasher.verify_password(password, user.hashed_password):
                return False
            await uow.users.update_login_time(user.id)
            await uow.commit()
            return True

    async def change_password(self, user_id: uuid.UUID, new_password: str) -> None:
        hashed = self.hasher.hash_password(new_password)
        async with self.uow as uow:
            user = await uow.users.get_by_id(user_id)
            if not user:
                raise ValueError('User not found')
            user.hashed_password = hashed
            await uow.users.update(user)
            await uow.commit()

    async def activate_user(self, user_id: uuid.UUID) -> None:
        async with self.uow as uow:
            await uow.users.activate(user_id)
            await uow.commit()

    async def deactivate_user(self, user_id: uuid.UUID) -> None:
        async with self.uow as uow:
            await uow.users.deactivate(user_id)
            await uow.commit()

    async def verify_email(self, user_id: uuid.UUID) -> None:
        async with self.uow as uow:
            await uow.users.verify_email(user_id)
            await uow.commit()

    async def get_user_by_email(self, email: str) -> User | None:
        async with self.uow as uow:
            return await uow.users.get_by_email(email)

    async def get_user_by_id(self, user_id: uuid.UUID) -> User | None:
        async with self.uow as uow:
            return await uow.users.get_by_id(user_id)

    async def get_user_by_username(self, username: str) -> User | None:
        async with self.uow as uow:
            return await uow.users.get_by_username(username)

    async def list_users(self, only_active: bool = False) -> list[User]:
        async with self.uow as uow:
            return await uow.users.list_all(only_active=only_active)
