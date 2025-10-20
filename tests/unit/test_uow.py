from unittest.mock import AsyncMock, MagicMock

import pytest

from src.service_layer.uow import SqlAlchemyUnitOfWork
from tests.conftest import FakeRepoFactory


class TestSqlAlchemyUnitOfWork:
    @pytest.mark.asyncio
    async def test_uow_context_manager_commit(self):
        # подготовка
        fake_session = AsyncMock()
        session_factory = MagicMock(return_value=fake_session)
        repo_factory = FakeRepoFactory()

        # когда используем контекстный менеджер без ошибки
        async with SqlAlchemyUnitOfWork(session_factory, repo_factory) as uow:
            assert uow.session is fake_session
            assert uow.users == 'fake_repo'

        # тогда commit должен быть вызван, rollback нет
        fake_session.commit.assert_called_once()
        fake_session.rollback.assert_not_called()
        fake_session.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_uow_context_manager_rollback_on_exception(self):
        fake_session = AsyncMock()
        session_factory = MagicMock(return_value=fake_session)
        repo_factory = FakeRepoFactory()

        class Error(Exception):
            pass

        with pytest.raises(Error):
            async with SqlAlchemyUnitOfWork(session_factory, repo_factory) as uow:
                raise Error()

        # тогда rollback должен быть вызван, commit нет
        fake_session.rollback.assert_called_once()
        fake_session.commit.assert_not_called()
        fake_session.close.assert_called_once()
