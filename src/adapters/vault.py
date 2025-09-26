import os
from typing import Any

import hvac

from src.adapters.interfaces import ISecretsProvider


class VaultClient(ISecretsProvider):
    """
    Клиент для взаимодействия с key-value хранилищем секретов HashiCorp Vault.

    Этот класс реализует интерфейс ISecretsProvider и предоставляет методы для
    безопасного получения секретов с сервера Vault. Поддерживает аутентификацию
    с использованием токена.

    Args:
        ISecretsProvider: Интерфейс, определяющий контракт для провайдеров секретов.
    """

    def __init__(self, addr: str | None = None, token_file: str | None = None):
        """
        Инициализирует клиент Vault с параметрами подключения.

        Args:
            addr: URL сервера Vault. Если не указан, будет прочитан из
                переменной окружения VAULT_ADDR.
            token_file: Путь к файлу с токеном аутентификации Vault.
                Если не указан, будет прочитан из переменной окружения VAULT_TOKEN_FILE.

        Raises:
            ValueError: Если не указаны параметры addr/token_file и соответствующие
                переменные окружения отсутствуют.
        """
        self._addr = addr or os.environ.get("VAULT_ADDR")
        self._token_file = token_file or os.environ.get("VAULT_TOKEN_FILE")
        self._client = self._init_client()

    def _init_client(self) -> hvac.Client:
        """
        Инициализирует и аутентифицирует клиент Vault.

        Returns:
            hvac.Client: Аутентифицированный экземпляр клиента Vault.

        Raises:
            ValueError: Если отсутствует обязательная конфигурация.
            ConnectionError: Если не удалось аутентифицироваться в Vault.
            FileNotFoundError: Если не удалось прочитать файл с токеном.
        """
        if not self._addr or not self._token_file:
            raise ValueError(
                "VAULT_ADDR и VAULT_TOKEN_FILE должны быть заданы",
            )

        with open(self._token_file) as f:
            token = f.read().strip()

        client = hvac.Client(url=self._addr, token=token)
        if not client.is_authenticated():
            raise ConnectionError("Vault authentication failed")

        return client

    def read_secret(self, path: str) -> dict[str, Any]:
        """
        Читает секрет из key-value хранилища Vault.

        Args:
            path: Путь к секрету в Vault (например, 'secret/data/myapp/config').

        Returns:
            dict[str, Any]: Словарь с данными секрета.

        Note:
            Метод предполагает использование KV Secrets Engine v2.
            Данные секрета должны находиться в поле 'data.data' ответа.
        """
        secret = self._client.secrets.kv.v2.read_secret_version(path=path)
        return secret["data"]["data"]
