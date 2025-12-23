import datetime


class DomainError(Exception):
    code: str = 'DOMAIN_ERROR'
    message: str = 'Domain error'

    def __init__(self, details=None):
        self.details = details
        super().__init__(self.message)


class UserNotFoundError(DomainError):
    code = 'USER_NOT_FOUND'
    message = 'User not found'


class InvalidCredentialsError(DomainError):
    code = 'INVALID_CREDENTIALS'
    message = 'Invalid credentials'

    def __init__(self, remaining_attempts: int | None = None):
        super().__init__(
            details={
                'remaining_attempts': remaining_attempts,
            },
        )


class EmailAlreadyRegisteredError(DomainError):
    code = 'EMAIL_ALREADY_REGISTERED'
    message = 'Email already registered'


class UsernameAlreadyTakenError(DomainError):
    code = 'USERNAME_ALREADY_TAKEN'
    message = 'Username already taken'


class MaxLoginAttemptsExceeded(DomainError):
    code = 'MAX_LOGIN_ATTEMPTS'
    message = 'Maximum login attempts reached'

    def __init__(
        self,
        *,
        max_attempts: int,
        retry_after: datetime.timedelta,
    ):
        super().__init__(
            details={
                'max_attempts': max_attempts,
                'retry_after_seconds': int(retry_after.total_seconds()),
            },
        )


class UserLockedError(DomainError):
    code = 'USER_LOCKED'
    message = 'User is locked'

    def __init__(self, *, retry_after: datetime.timedelta):
        super().__init__(
            details={
                'retry_after_seconds': int(retry_after.total_seconds()),
            },
        )


class EmailAlreadyVerifiedError(DomainError):
    code = 'EMAIL_ALREADY_VERIFIED'
    message = 'Email is already verified'


class UserDisabledError(DomainError):
    code = 'USER_DISABLED'
    message = 'User is disabled'


class SamePasswordError(DomainError):
    code = 'SAME_PASSWORD'
    message = 'Password is the same as the old one'


class SameEmailError(DomainError):
    code = 'SAME_EMAIL'
    message = 'Email is the same as the old one'


class InvalidEmailError(DomainError):
    code = 'INVALID_EMAIL'
    message = 'Invalid email format'


class InvalidFirstNameError(DomainError):
    code = 'INVALID_FIRST_NAME'
    message = 'Invalid first name format'


class InvalidLastNameError(DomainError):
    code = 'INVALID_LAST_NAME'
    message = 'Invalid last name format'


class InvalidUsernameError(DomainError):
    code = 'INVALID_USERNAME'
    message = 'Invalid username format'


class EmailNotVerifiedError(DomainError):
    code = 'EMAIL_NOT_VERIFIED'
    message = 'Email is not verified'
