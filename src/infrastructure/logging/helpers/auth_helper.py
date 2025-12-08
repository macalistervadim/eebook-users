import logging

from src.utils.auth_events import AuthEvent

logger = logging.getLogger(__name__)


def auth_log(action: AuthEvent, description: str = '', **details):
    """Унифицированный логгер для событий аутентификации.

    Пример:
        [REFRESH_ISSUED] Выпущен новый refresh-token | user_id=... | refresh_id=...

    Args:
        action: Короткий код события.
        description: Короткое описание события.
        **details: параметры (ключ=значение)

    """
    base = f'[{action.value}]'
    if description:
        base += f' {description}'
    if details:
        base += ' | ' + ' | '.join(f'{k}={v}' for k, v in details.items())
    logger.debug(base)
