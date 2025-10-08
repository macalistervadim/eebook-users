from unittest.mock import patch, mock_open

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, clear_mappers

from src.adapters.orm import metadata, start_mappers
from src.adapters.vault import VaultClient


@pytest.fixture
def in_memory_db():
    engine = create_engine('sqlite:///:memory:')
    metadata.create_all(engine)
    return engine


@pytest.fixture
def session_factory(in_memory_db):
    start_mappers()
    yield sessionmaker(bind=in_memory_db)

    clear_mappers()


@pytest.fixture
def session(session_factory):
    return session_factory()


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
