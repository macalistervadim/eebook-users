import logging
import os
from typing import Any, Final

import hvac

from src.adapters.exceptions.vault_exceptions import (
    VaultAuthenticationError,
    VaultConnectionError,
    VaultError,
    VaultPermissionError,
    VaultSecretNotFoundError,
    VaultTokenError,
)

logger = logging.getLogger(__name__)


VAULT_ADDR_ENV_NAME: Final[str] = 'VAULT_ADDR'
VAULT_TOKEN_FILE_ENV_NAME: Final[str] = 'VAULT_TOKEN_FILE'


class VaultClient:
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

    def __init__(self, addr: str | None = None, token_file: str | None = None) -> None:
        f"""
        Инициализирует клиент Vault с параметрами подключения.

        Args:
            addr: URL сервера Vault. Если не указан, будет прочитан из
                переменной окружения {VAULT_ADDR_ENV_NAME}.
            token_file: Путь к файлу с токеном аутентификации Vault.
                Если не указан, будет прочитан из переменной окружения {VAULT_TOKEN_FILE_ENV_NAME}.

        Raises:
            ValueError: Если не указаны параметры addr/token_file и соответствующие
                переменные окружения отсутствуют.
        """

        self._addr = addr or os.environ.get(VAULT_ADDR_ENV_NAME)
        self._token_file = token_file or os.environ.get(VAULT_TOKEN_FILE_ENV_NAME)
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
            logger.error(
                f'Не заданы переменные окружения {VAULT_ADDR_ENV_NAME} '
                f'и {VAULT_TOKEN_FILE_ENV_NAME}',
            )
            raise VaultError(
                f'Переменные окружения {VAULT_ADDR_ENV_NAME} и '
                f'{VAULT_TOKEN_FILE_ENV_NAME} должны быть заданы',
            )

        try:
            with open(self._token_file) as f:
                token = f.read().strip()

            if not token:
                logger.error('Отсутствие токена при инициализации Vault-клиента')
                raise VaultTokenError('Токен не может быть пустым')

            client = hvac.Client(url=self._addr, token=token)

            if not client.is_authenticated():
                logger.error('Ошибка при аутентификации в Vault-клиенте')
                raise VaultAuthenticationError('Не удалось аутентифицироваться в Vault')

            logger.info('Vault-клиент успешно аутентифицирован')
            return client

        except FileNotFoundError:
            logger.exception(f'Файл с токеном для Vault-клиента не найден: {self._token_file}')
            raise VaultTokenError(f'Файл с токеном не найден: {self._token_file}')
        except PermissionError:
            logger.exception(f'Нет прав на чтение токена Vault-клиентом: {self._token_file}')
            raise VaultPermissionError(f'Нет прав на чтение токена: {self._token_file}')
        except Exception as e:
            if 'connection' in str(e).lower():
                logger.exception(f'Не удалось подключиться к Vault: {e}')
                raise VaultConnectionError(f'Не удалось подключиться к Vault: {e}')
            logger.exception(f'Ошибка при инициализации клиента Vault: {e}')
            raise VaultError(f'Ошибка при инициализации клиента Vault: {e}')

    async def get_secret(self, path: str, key: str | None = None) -> dict[str, Any]:  # type: ignore
        """
        Получает секрет из Vault по указанному пути.

        Пример:
            # Получение секрета
            secret = vault.read_secret('eebook/users/database')
            # Результат: {'username': 'admin', 'password': 's3cr3t'} # pragma: allowlist secret

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
            logger.debug('Успешно прочитан секрет из Vault')
            return secret['data']['data']
        except Exception as e:
            if '404' in str(e):
                logger.error(
                    f'Не удалось обнаружить переданный секрет в Vault-хранилище по пути: {path}',
                )
                raise VaultSecretNotFoundError(f'Секрет не найден: {path}')
            logger.exception('Ошибка при чтении Vault-секрета')
            raise VaultError(f'Ошибка при чтении секрета: {e}')
