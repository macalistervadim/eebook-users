import abc
import uuid

from src.adapters.abc_classes import ABCAuthService, ABCTimeProvider
from src.adapters.interfaces import IPasswordHasher
from src.domain.exceptions.exceptions import EmailAlreadyRegisteredError, UsernameAlreadyTakenError, UserNotFoundError, \
    InvalidCredentialsError
from src.domain.model import User

from src.schemas.api.auth import TokenPair
from src.service_layer.uow import AbstractUnitOfWork


class ABCUserService(abc.ABC):
    """Абстрактный сервис для работы с пользователями.

    Определяет интерфейс для операций с пользователями,
    включая регистрацию, вход, управление статусом и получение информации.
    """

    @abc.abstractmethod
    async def register_user(
        self,
        first_name: str,
        last_name: str,
        email: str,
        username: str,
        password: str,
        fingerprint: str,
    ) -> tuple[User, TokenPair]:
        """Создаёт нового пользователя и выдаёт пару токенов.

        Args:
            first_name: Имя пользователя.
            last_name: Фамилия пользователя.
            email: Email пользователя.
            username: Логин пользователя.
            password: Пароль пользователя.
            fingerprint: Уникальный идентификатор устройства/браузера.

        Returns:
            Tuple[User, TokenPair]: Созданный пользователь и JWT-пара.

        Raises:
            NotImplementedError: Если метод не реализован.

        """
        raise NotImplementedError

    @abc.abstractmethod
    async def login(
        self,
        email: str,
        password: str,
        fingerprint: str,
    ) -> TokenPair | None:
        """Аутентифицирует пользователя и выдаёт JWT-пару.

        Args:
            email: Email пользователя.
            password: Пароль пользователя.
            fingerprint: Уникальный идентификатор устройства/браузера.

        Returns:
            TokenPair | None: Пара токенов или None при неуспехе.

        Raises:
            NotImplementedError: Если метод не реализован.

        """
        raise NotImplementedError

    @abc.abstractmethod
    async def remove_user(self, user_id: uuid.UUID) -> None:
        """Удаляет пользователя по ID.

        Args:
            user_id: ID пользователя.

        Raises:
            NotImplementedError: Если метод не реализован.

        """
        raise NotImplementedError

    # @abc.abstractmethod
    # async def change_password(self, user_id: uuid.UUID, new_password: str) -> None:
    #     """Меняет пароль пользователя.
    #
    #     Args:
    #         user_id: ID пользователя.
    #         new_password: Новый пароль.
    #
    #     Raises:
    #         ValueError: Если пользователь не найден.
    #         NotImplementedError: Если метод не реализован.
    #
    #     """
    #     raise NotImplementedError

    @abc.abstractmethod
    async def activate_user(self, user_id: uuid.UUID) -> None:
        """Активирует пользователя.

        Args:
            user_id: ID пользователя.

        Raises:
            ValueError: Если пользователь не найден.
            NotImplementedError: Если метод не реализован.

        """
        raise NotImplementedError

    @abc.abstractmethod
    async def deactivate_user(self, user_id: uuid.UUID) -> None:
        """Деактивирует пользователя.

        Args:
            user_id: ID пользователя.

        Raises:
            ValueError: Если пользователь не найден.
            NotImplementedError: Если метод не реализован.

        """
        raise NotImplementedError

    @abc.abstractmethod
    async def verify_email(self, user_id: uuid.UUID) -> None:
        """Подтверждает email пользователя.

        Args:
            user_id: ID пользователя.

        Raises:
            ValueError: Если пользователь не найден.
            NotImplementedError: Если метод не реализован.

        """
        raise NotImplementedError

    @abc.abstractmethod
    async def get_user_by_email(self, email: str) -> User | None:
        """Находит пользователя по email.

        Args:
            email: Email пользователя.

        Returns:
            User | None: Пользователь или None.

        Raises:
            NotImplementedError: Если метод не реализован.

        """
        raise NotImplementedError

    @abc.abstractmethod
    async def get_user_by_id(self, user_id: uuid.UUID) -> User | None:
        """Находит пользователя по ID.

        Args:
            user_id: ID пользователя.

        Returns:
            User | None: Пользователь или None.

        Raises:
            NotImplementedError: Если метод не реализован.

        """
        raise NotImplementedError

    @abc.abstractmethod
    async def get_user_by_username(self, username: str) -> User | None:
        """Находит пользователя по username.

        Args:
            username: Логин пользователя.

        Returns:
            User | None: Пользователь или None.

        Raises:
            NotImplementedError: Если метод не реализован.

        """
        raise NotImplementedError

    @abc.abstractmethod
    async def list_users(self, only_active: bool = False) -> list[User]:
        """Возвращает список пользователей.

        Args:
            only_active: Если True, возвращает только активных пользователей.

        Returns:
            List[User]: Список пользователей.

        Raises:
            NotImplementedError: Если метод не реализован.

        """
        raise NotImplementedError


class UserService(ABCUserService):
    """Сервисный слой для работы с пользователями (бизнес-логика)."""

    def __init__(
        self,
        uow: AbstractUnitOfWork,
        hasher: IPasswordHasher,
        time_provider: ABCTimeProvider,
        auth_service: ABCAuthService,
    ) -> None:
        self.uow = uow
        self.hasher = hasher
        self.time_provider = time_provider
        self.auth_service = auth_service

    async def register_user(
        self,
        first_name: str,
        last_name: str,
        email: str,
        username: str,
        password: str,
        fingerprint: str,
    ) -> tuple[User, TokenPair]:
        async with self.uow as uow:
            email = email.lower().strip()
            
            existing = await uow.users.get_by_email(email)
            if existing:
                raise EmailAlreadyRegisteredError(email)
            if username and await uow.users.get_by_username(username):
                raise UsernameAlreadyTakenError(username)

            hashed = self.hasher.hash_password(password)
            now = self.time_provider.now()

            user = User(
                user_id=None,
                first_name=first_name,
                last_name=last_name,
                email=email,
                username=username,
                hashed_password=hashed,
                created_at=now,
                updated_at=now,
                last_login_at=now,
            )
            
            await uow.users.add(user)
            await uow.commit()

            token_pair = await self.auth_service.create_token_pair(
                uow=uow,
                user_id=user.id,
                fingerprint=fingerprint,
            )

            return user, token_pair

    async def remove_user(self, user_id: uuid.UUID) -> None:
        async with self.uow as uow:
            await uow.users.remove(user_id)
            await uow.commit()

    async def login(self, email: str, password: str, fingerprint: str) -> TokenPair | None:
        async with self.uow as uow:
            user = await uow.users.get_by_email(email)
       
            if not user:
                raise InvalidCredentialsError()

            if not self.hasher.verify_password(password, user.hashed_password):
                raise InvalidCredentialsError()

            user.update_login_time(self.time_provider.now())
            await uow.users.update(user)
            await uow.commit()

            token_pair = await self.auth_service.create_token_pair(
                uow=uow,
                user_id=user.id,
                fingerprint=fingerprint,
            )

            await uow.commit()
            return token_pair

    # async def change_password(self, user_id: uuid.UUID, new_password: str) -> None:
    #     hashed = self.hasher.hash_password(new_password)
    #     async with self.uow as uow:
    #         user = await uow.users.get_by_id(user_id)
    #         if not user:
    #             raise ValueError('User not found')
    #         user.change_password(hashed)
    #         await uow.users.update(user)
    #         await uow.commit()

    async def activate_user(self, user_id: uuid.UUID) -> None:
        async with self.uow as uow:
            user = await uow.users.get_by_id(user_id)
            if not user:
                raise ValueError('User not found')
            user.activate(self.time_provider.now())
            await uow.users.update(user)
            await uow.commit()

    async def deactivate_user(self, user_id: uuid.UUID) -> None:
        async with self.uow as uow:
            user = await uow.users.get_by_id(user_id)
            if not user:
                raise ValueError('User not found')
            user.deactivate(self.time_provider.now())
            await uow.users.update(user)
            await uow.commit()

    async def verify_email(self, user_id: uuid.UUID) -> None:
        async with self.uow as uow:
            user = await uow.users.get_by_id(user_id)
            if not user:
                raise ValueError('User not found')
            user.verify_email(self.time_provider.now())
            await uow.users.update(user)
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
