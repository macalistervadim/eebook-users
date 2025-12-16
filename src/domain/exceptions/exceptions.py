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


class EmailAlreadyRegisteredError(DomainError):
    code = 'EMAIL_ALREADY_REGISTERED'
    message = 'Email already registered'


class UsernameAlreadyTakenError(DomainError):
    code = 'USERNAME_ALREADY_TAKEN'
    message = 'Username already taken'
