import uuid
import pytest
import datetime

from src.adapters.repository import SQLAlchemyUsersRepository
from src.domain.model import User, IPasswordHasher


@pytest.mark.asyncio
class TestSQLAlchemyUsersRepository:
    async def test_add_user(self, repo, async_session, sample_user):
        await repo.add(sample_user)
        await async_session.commit()
        fetched = await repo.get_by_id(sample_user.id)
        assert fetched is not None
        assert fetched.email == sample_user.email

    async def test_get_by_email(self, repo, async_session, sample_user):
        await repo.add(sample_user)
        await async_session.commit()
        fetched = await repo.get_by_email('vadim@example.com')
        assert fetched.username == sample_user.username

    async def test_get_by_username(self, repo, async_session, sample_user):
        await repo.add(sample_user)
        await async_session.commit()
        fetched = await repo.get_by_username('vadim')
        assert fetched.email == sample_user.email

    async def test_list_all_users(self, repo, async_session, sample_user):
        await repo.add(sample_user)
        await async_session.commit()
        all_users = await repo.list_all()
        assert len(all_users) == 1
        active_users = await repo.list_all(only_active=True)
        assert len(active_users) == 1

    async def test_update_user(self, repo, async_session, sample_user):
        await repo.add(sample_user)
        await async_session.commit()
        sample_user.first_name = 'Updated'
        await repo.update(sample_user)
        await async_session.commit()
        updated = await repo.get_by_id(sample_user.id)
        assert updated.first_name == 'Updated'

    async def test_remove_user(self, repo, async_session, sample_user):
        await repo.add(sample_user)
        await async_session.commit()
        await repo.remove(sample_user.id)
        await async_session.commit()
        assert await repo.get_by_id(sample_user.id) is None

    async def test_activate_deactivate_user(self, repo, async_session, sample_user):
        sample_user.is_active = False
        await repo.add(sample_user)
        await async_session.commit()

        await repo.activate(sample_user.id)
        await async_session.commit()
        assert (await repo.get_by_id(sample_user.id)).is_active is True

        await repo.deactivate(sample_user.id)
        await async_session.commit()
        assert (await repo.get_by_id(sample_user.id)).is_active is False

    async def test_verify_email_user(self, repo, async_session, sample_user):
        sample_user.is_verified = False
        await repo.add(sample_user)
        await async_session.commit()

        await repo.verify_email(sample_user.id)
        await async_session.commit()
        assert (await repo.get_by_id(sample_user.id)).is_verified is True

    async def test_set_password_and_verify_password(self, repo, async_session, sample_user, hasher):
        await repo.add(sample_user)
        await async_session.commit()

        await repo.set_password(sample_user.id, 'new_pass')
        await async_session.commit()
        stored = await repo.get_by_id(sample_user.id)
        assert hasher.verify_password('new_pass', stored.hashed_password)

        # проверка неправильного пароля
        assert not await repo.verify_password(sample_user.id, 'wrong_pass')
