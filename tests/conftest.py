import uuid
from unittest.mock import patch, mock_open, AsyncMock

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from src.adapters.factory import ABCUsersRepositoryFactory
from src.adapters.orm import metadata
from src.adapters.repository import SQLAlchemyUsersRepository
from src.adapters.vault import VaultClient
from src.domain.model import User


@pytest_asyncio.fixture
async def in_memory_async_db():
    engine = create_async_engine('sqlite+aiosqlite:///:memory:', echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(metadata.drop_all)


@pytest_asyncio.fixture
async def async_session_factory(in_memory_async_db):
    yield async_sessionmaker(bind=in_memory_async_db, expire_on_commit=False)


@pytest_asyncio.fixture
async def async_session(async_session_factory):
    async with async_session_factory() as session:
        yield session


@pytest_asyncio.fixture
async def repo(async_session, hasher):
    return SQLAlchemyUsersRepository(async_session, hasher)


@pytest.fixture
def mock_vault_client():
    with (
        patch('builtins.open', mock_open(read_data='fake-token')),
        patch('src.adapters.vault.hvac.Client') as MockClient,
    ):
        mock_client = MockClient.return_value
        mock_client.is_authenticated.return_value = True
        mock_client.secrets.kv.v2.read_secret_version.return_value = {
            'data': {'data': {'username': 'admin', 'password': '123'}}
        }

        vc = VaultClient(addr='http://fake', token_file='/fake/token')
        yield vc


@pytest.fixture
def sample_user(hasher):
    return User(
        user_id=uuid.uuid4(),
        first_name='Vadim',
        last_name='Startsev',
        email='vadim@example.com',
        username='vadim',
        hashed_password=hasher.hash_password('123'),
        _hasher=hasher,
    )


class FakeHasher:
    def hash_password(self, password: str) -> str:
        return 'hashed_' + password

    def verify_password(self, password: str, hashed_password: str) -> bool:
        return hashed_password == 'hashed_' + password


@pytest.fixture
def hasher():
    return FakeHasher()


@pytest.fixture
def fake_uow():
    uow = AsyncMock()
    uow.users = AsyncMock()
    uow.commit = AsyncMock()
    # Настраиваем все методы репозитория как асинхронные
    uow.users.add = AsyncMock()
    uow.users.remove = AsyncMock()
    uow.users.activate = AsyncMock()
    uow.users.deactivate = AsyncMock()
    uow.users.get_by_email = AsyncMock()
    uow.users.get_by_id = AsyncMock()
    uow.users.update = AsyncMock()
    uow.users.update_login_time = AsyncMock()
    uow.users.list_all = AsyncMock()
    uow.users.verify_email = AsyncMock()
    uow.__aenter__.return_value = uow
    uow.__aexit__.return_value = None
    return uow


class FakeRepoFactory(ABCUsersRepositoryFactory):
    def create(self, session):
        return 'fake_repo'
