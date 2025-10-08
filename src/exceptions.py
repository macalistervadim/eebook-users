class BootstrapInitializationError(Exception):
    """Вызывается при неполадках в инициализации проекта."""


class DatabaseCreateTablesError(Exception):
    """Вызывается при неуспешном создании таблиц в базе данных."""
