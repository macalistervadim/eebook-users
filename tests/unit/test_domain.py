import datetime
from freezegun import freeze_time


class TestUserModel:
    @freeze_time('2025-10-17 12:00:00')
    def test_update_login_time(self, sample_user):
        sample_user.update_login_time()
        assert sample_user.last_login_at == datetime.datetime(
            2025, 10, 17, 12, 0, 0, tzinfo=datetime.UTC
        )

    @freeze_time('2025-10-17 12:01:00')
    def test_activate(self, sample_user):
        sample_user.is_active = False
        sample_user.activate()
        assert sample_user.is_active is True
        assert sample_user.updated_at == datetime.datetime(
            2025, 10, 17, 12, 1, 0, tzinfo=datetime.UTC
        )

    @freeze_time('2025-10-17 12:02:00')
    def test_deactivate(self, sample_user):
        sample_user.is_active = True
        sample_user.deactivate()
        assert sample_user.is_active is False
        assert sample_user.updated_at == datetime.datetime(
            2025, 10, 17, 12, 2, 0, tzinfo=datetime.UTC
        )

    @freeze_time('2025-10-17 12:03:00')
    def test_verify_email(self, sample_user):
        sample_user.is_verified = False
        sample_user.verify_email()
        assert sample_user.is_verified is True
        assert sample_user.updated_at == datetime.datetime(
            2025, 10, 17, 12, 3, 0, tzinfo=datetime.UTC
        )

    def test_verify_password_success(self, sample_user):
        assert sample_user.verify_password('123') is True

    def test_verify_password_fail(self, sample_user):
        assert sample_user.verify_password('wrong_password') is False

    def test_set_password(self, sample_user):
        sample_user.set_password('newpass')
        assert sample_user.hashed_password == 'hashed_newpass'

    def test_activate_already_active(self, sample_user):
        sample_user.is_active = True
        old_updated = sample_user.updated_at
        sample_user.activate()
        # Должно оставаться активным и обновлять updated_at
        assert sample_user.is_active is True
        assert sample_user.updated_at != old_updated

    def test_deactivate_already_inactive(self, sample_user):
        sample_user.is_active = False
        old_updated = sample_user.updated_at
        sample_user.deactivate()
        # Должно оставаться неактивным и обновлять updated_at
        assert sample_user.is_active is False
        assert sample_user.updated_at != old_updated

    def test_verify_email_already_verified(self, sample_user):
        sample_user.is_verified = True
        old_updated = sample_user.updated_at
        sample_user.verify_email()
        # Должно оставаться верифицированным и обновлять updated_at
        assert sample_user.is_verified is True
        assert sample_user.updated_at != old_updated

    def test_set_password_empty_string(self, sample_user):
        sample_user.set_password('')
        assert sample_user.hashed_password == 'hashed_'
