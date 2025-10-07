class DatabaseConnectionError(Exception):
    """Ошибка подключения к базе данных."""

    pass

class DatabaseTimeoutError(Exception):
    """Ошибка таймаута подключения к базе данных."""

    pass

class DatabaseArgumentError(Exception):
    """Ошибка аргументов подключения к базе данных."""

    pass
