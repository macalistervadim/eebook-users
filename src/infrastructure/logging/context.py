"""Request-scoped logging context helpers."""

from contextvars import ContextVar, Token

request_id_var: ContextVar[str] = ContextVar('request_id', default='-')
user_id_var: ContextVar[str] = ContextVar('user_id', default='-')


def set_request_id(value: str) -> Token[str]:
    return request_id_var.set(value)


def reset_request_id(token: Token[str]) -> None:
    request_id_var.reset(token)


def set_user_id(value: str) -> Token[str]:
    return user_id_var.set(value)


def reset_user_id(token: Token[str]) -> None:
    user_id_var.reset(token)
