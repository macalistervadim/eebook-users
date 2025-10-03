"""
Классы исключений для config, bootstrap
"""


class ConfigurationError(Exception):
    """
    Вызывается при неполадках в настройках проекта
    """


class DatabaseError(Exception):
    """Базовое исключение для ошибок базы данных."""
