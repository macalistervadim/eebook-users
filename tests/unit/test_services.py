from uuid import uuid4

import pytest

from src.domain.model import User
from src.service_layer.users_service import UserService


@pytest.mark.asyncio
class TestUserService:
    async def test_register_user(self, fake_uow, hasher):
        service = UserService(fake_uow, hasher)

        user = await service.register_user(
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            username="johnny",
            password="12345"
        )

        assert user.hashed_password == "hashed_12345"
        assert user.first_name == "John"
        assert user.last_name == "Doe"

        fake_uow.users.add.assert_awaited_once_with(user)
        fake_uow.commit.assert_awaited_once()

    async def test_login_success(self, fake_uow, hasher):
        user = User(
            user_id=uuid4(),
            first_name="John",
            last_name="Doe",
            email="a@b.com",
            username="johnny",
            hashed_password="hashed_12345",
            _hasher=hasher
        )
        fake_uow.users.get_by_email.return_value = user
        service = UserService(fake_uow, hasher)

        result = await service.login(email="a@b.com", password="12345")

        assert result is True
        fake_uow.users.get_by_email.assert_awaited_once_with("a@b.com")
        fake_uow.users.update_login_time.assert_awaited_once_with(user.id)
        fake_uow.commit.assert_awaited_once()

    async def test_login_fail_wrong_password(self, fake_uow, hasher):
        user = User(
            user_id=uuid4(),
            first_name="John",
            last_name="Doe",
            email="a@b.com",
            username="johnny",
            hashed_password="hashed_12345",
            _hasher=hasher
        )
        fake_uow.users.get_by_email.return_value = user
        service = UserService(fake_uow, hasher)

        result = await service.login(email="a@b.com", password="wrong")

        assert result is False
        fake_uow.commit.assert_not_awaited()

    async def test_login_fail_user_not_found(self, fake_uow, hasher):
        fake_uow.users.get_by_email.return_value = None
        service = UserService(fake_uow, hasher)

        result = await service.login(email="a@b.com", password="12345")

        assert result is False
        fake_uow.commit.assert_not_awaited()

    async def test_remove_user(self, fake_uow, hasher):
        service = UserService(fake_uow, hasher)
        user_id = uuid4()

        await service.remove_user(user_id)

        fake_uow.users.remove.assert_awaited_once_with(user_id)
        fake_uow.commit.assert_awaited_once()

    async def test_change_password(self, fake_uow, hasher):
        service = UserService(fake_uow, hasher)
        user_id = uuid4()
        user = User(
            user_id=user_id,
            first_name="John",
            last_name="Doe",
            email="a@b.com",
            username="johnny",
            hashed_password="old_hash",
            _hasher=hasher
        )
        fake_uow.users.get_by_id.return_value = user

        await service.change_password(user_id, "new_password")

        assert user.hashed_password == "hashed_new_password"
        fake_uow.users.update.assert_awaited_once_with(user)
        fake_uow.commit.assert_awaited_once()

    async def test_activate_deactivate_user(self, fake_uow, hasher):
        service = UserService(fake_uow, hasher)
        user_id = uuid4()

        await service.activate_user(user_id)
        fake_uow.users.activate.assert_awaited_once_with(user_id)
        fake_uow.commit.assert_awaited_once()

        fake_uow.reset_mock()

        await service.deactivate_user(user_id)
        fake_uow.users.deactivate.assert_awaited_once_with(user_id)
        fake_uow.commit.assert_awaited_once()

    async def test_verify_email(self, fake_uow, hasher):
        service = UserService(fake_uow, hasher)
        user_id = uuid4()

        await service.verify_email(user_id)
        fake_uow.users.verify_email.assert_awaited_once_with(user_id)
        fake_uow.commit.assert_awaited_once()

    async def test_register_user_empty_password(self, fake_uow, hasher):
        service = UserService(fake_uow, hasher)
        user = await service.register_user(
            first_name="A",
            last_name="B",
            email="c@d.com",
            username="abc",
            password=""
        )
        assert user.hashed_password == "hashed_"
        fake_uow.users.add.assert_awaited_once_with(user)
        fake_uow.commit.assert_awaited_once()

    async def test_login_with_empty_password(self, fake_uow, hasher):
        user = User(
            user_id=uuid4(),
            first_name="X",
            last_name="Y",
            email="x@y.com",
            username="xy",
            hashed_password="hashed_123",
            _hasher=hasher
        )
        fake_uow.users.get_by_email.return_value = user
        service = UserService(fake_uow, hasher)

        result = await service.login(email="x@y.com", password="")
        assert result is False
        fake_uow.commit.assert_not_awaited()

    async def test_change_password_user_not_found(self, fake_uow, hasher):
        fake_uow.users.get_by_id.return_value = None
        service = UserService(fake_uow, hasher)
        with pytest.raises(ValueError):
            await service.change_password(uuid4(), "newpass")
        fake_uow.commit.assert_not_awaited()

    async def test_list_users_empty(self, fake_uow, hasher):
        fake_uow.users.list_all.return_value = []
        service = UserService(fake_uow, hasher)
        res = await service.list_users(only_active=True)
        assert res == []
        fake_uow.users.list_all.assert_awaited_once_with(only_active=True)

    async def test_activate_deactivate_nonexistent_user(self, fake_uow, hasher):
        service = UserService(fake_uow, hasher)
        user_id = uuid4()

        # Всё равно вызываем activate/deactivate на репозиторий
        await service.activate_user(user_id)
        fake_uow.users.activate.assert_awaited_once_with(user_id)
        fake_uow.commit.assert_awaited_once()

        fake_uow.reset_mock()

        await service.deactivate_user(user_id)
        fake_uow.users.deactivate.assert_awaited_once_with(user_id)
        fake_uow.commit.assert_awaited_once()

    async def test_verify_email_nonexistent_user(self, fake_uow, hasher):
        service = UserService(fake_uow, hasher)
        user_id = uuid4()
        await service.verify_email(user_id)
        fake_uow.users.verify_email.assert_awaited_once_with(user_id)
        fake_uow.commit.assert_awaited_once()

    async def test_login_user_not_found_empty_string_email(self, fake_uow, hasher):
        fake_uow.users.get_by_email.return_value = None
        service = UserService(fake_uow, hasher)
        result = await service.login("", "123")
        assert result is False
        fake_uow.commit.assert_not_awaited()
