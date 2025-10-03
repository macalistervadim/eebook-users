class VaultError(Exception):
    """Базовое исключение для ошибок Vault."""
    pass


class VaultConnectionError(VaultError):
    """Ошибка подключения к Vault."""
    pass


class VaultAuthenticationError(VaultError):
    """Ошибка аутентификации в Vault."""
    pass


class VaultSecretNotFoundError(VaultError):
    """Запрошенный секрет не найден в Vault."""
    pass


class VaultTokenError(VaultError):
    """Ошибка, связанная с токеном Vault."""
    pass


class VaultPermissionError(VaultError):
    """Ошибка прав доступа к ресурсу Vault."""
    pass
