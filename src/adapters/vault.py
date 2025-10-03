import logging
import os
from typing import Any

import hvac

from src.adapters.exceptions.vault_exceptions import (
    VaultAuthenticationError,
    VaultConnectionError,
    VaultError,
    VaultPermissionError,
    VaultSecretNotFoundError,
    VaultTokenError,
)
from src.adapters.interfaces import ISecretsProvider

logger = logging.getLogger(__name__)


class VaultClient(ISecretsProvider):
    """
    Клиент для работы с HashiCorp Vault - системой для безопасного хранения секретов.

    Позволяет получать секреты из Vault с использованием токена аутентификации.

    Пример использования:
        # Инициализация клиента
        vault = VaultClient(
            addr='http://localhost:8200',  # Адрес Vault сервера
            token_file='/path/to/token'    # Файл с токеном доступа
        )

        # Получение секрета
        secret = vault.read_secret('путь/к/секрету')

    Примечание:
        - Для работы требуется настроенный и запущенный сервер Vault
        - Токен доступа должен иметь права на чтение запрашиваемых секретов
        - По умолчанию используется KV Secrets Engine версии 2

    :param addr: Адрес Vault сервера (например, 'http://localhost:8200')
    :param token_file: Путь к файлу, содержащему токен аутентификации

    :raises VaultError: Общая ошибка при работе с Vault
    :raises VaultConnectionError: Ошибка подключения к Vault
    :raises VaultAuthenticationError: Ошибка аутентификации
    :raises VaultTokenError: Ошибка с токеном доступа
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
        self._addr = addr or os.environ.get('VAULT_ADDR')
        self._token_file = token_file or os.environ.get('VAULT_TOKEN_FILE')
        self._client = self._init_client()

    def _init_client(self) -> hvac.Client:
        """
        Создает и настраивает клиент для работы с Vault.

        :return: Аутентифицированный клиент Vault

        :raises VaultError: Если не удалось инициализировать клиент
        :raises VaultConnectionError: Если не удалось подключиться к серверу
        :raises VaultTokenError: Если возникла проблема с токеном
        :raises VaultAuthenticationError: Если аутентификация не удалась
        """
        if not self._addr or not self._token_file:
            raise VaultError('VAULT_ADDR и VAULT_TOKEN_FILE должны быть заданы')

        try:
            with open(self._token_file) as f:
                token = f.read().strip()

            if not token:
                raise VaultTokenError('Токен не может быть пустым')

            client = hvac.Client(url=self._addr, token=token)

            if not client.is_authenticated():
                raise VaultAuthenticationError('Не удалось аутентифицироваться в Vault')

            return client

        except FileNotFoundError:
            raise VaultTokenError(f'Файл с токеном не найден: {self._token_file}')
        except PermissionError:
            raise VaultPermissionError(f'Нет прав на чтение токена: {self._token_file}')
        except Exception as e:
            if 'connection' in str(e).lower():
                raise VaultConnectionError(f'Не удалось подключиться к Vault: {e}')
            raise VaultError(f'Ошибка при инициализации клиента Vault: {e}')

    # TODO: переписать на async, в контракте указан именно async
    # TODO: подумать по поводу конкретного наследования от протокола -
    #  мб стоит отказаться от лишнего наследования?
    def get_secret(self, path: str, key: str | None = None) -> dict[str, Any]:  # type: ignore
        """
        Получает секрет из Vault по указанному пути.

        Пример:
            # Получение секрета
            secret = vault.read_secret('eebook/users/database')
            # Результат: {'username': 'admin', 'password': 's3cr3t'}

            # Использование полученных данных
            db_user = secret['username']
            db_pass = secret['password']

        :param path: Путь к секрету в формате 'путь/к/секрету'.
                     Для KV v2 автоматически добавляется префикс 'data/' при необходимости.

        :return: Словарь с данными секрета

        :raises VaultSecretNotFoundError: Если секрет не найден по указанному пути
        :raises VaultPermissionError: Если недостаточно прав для доступа к секрету
        :raises VaultError: При других ошибках при чтении секрета

        Примечания:
            - Для KV v2 секреты хранятся в формате 'путь/к/секрету',
              а не в полном пути 'secret/data/путь/к/секрету'
            - Метод автоматически обрабатывает версионирование KV v2
        """
        try:
            secret = self._client.secrets.kv.v2.read_secret_version(path=path)
            return secret['data']['data']
        except Exception as e:
            if '404' in str(e):
                raise VaultSecretNotFoundError(f'Секрет не найден: {path}')
            raise VaultError(f'Ошибка при чтении секрета: {e}')
