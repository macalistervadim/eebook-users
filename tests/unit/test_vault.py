import pytest
from unittest.mock import patch, mock_open

from src.adapters.exceptions.vault_exceptions import (
    VaultSecretNotFoundError,
    VaultError,
    VaultTokenError,
    VaultAuthenticationError,
    VaultConnectionError,
)
from src.adapters.vault import VaultClient


class TestVaultClient:
    @pytest.mark.asyncio
    async def test_get_secret(self, mock_vault_client):
        result = await mock_vault_client.get_secret('some/path')
        assert result['username'] == 'admin'
        assert result['password'] == '123'

    @pytest.mark.asyncio
    async def test_get_secret_with_key(self, mock_vault_client):
        result = await mock_vault_client.get_secret('some/path', key='username')
        assert result == 'admin'

    @pytest.mark.asyncio
    async def test_get_secret_key_not_found(self, mock_vault_client):
        mock_vault_client._client.secrets.kv.v2.read_secret_version.return_value = {
            'data': {'data': {'username': 'admin'}}
        }
        with pytest.raises(VaultSecretNotFoundError):
            await mock_vault_client.get_secret('some/path', key='password')

    @pytest.mark.asyncio
    async def test_get_secret_not_found(self, mock_vault_client):
        mock_vault_client._client.secrets.kv.v2.read_secret_version.side_effect = (
            VaultSecretNotFoundError()
        )

        with pytest.raises(VaultSecretNotFoundError):
            await mock_vault_client.get_secret('some/path')

    @pytest.mark.asyncio
    async def test_get_secret_vault_error(self, mock_vault_client):
        mock_vault_client._client.secrets.kv.v2.read_secret_version.side_effect = VaultError()
        with pytest.raises(VaultError):
            await mock_vault_client.get_secret('some/path')

    def test_init_client_token_not_found(self):
        with pytest.raises(VaultTokenError):
            VaultClient(addr='http://fake', token_file='/nonexistent/path')

    def test_init_client_empty_token(self):
        with patch('builtins.open', mock_open(read_data='')):
            with pytest.raises(VaultTokenError):
                VaultClient(addr='http://fake', token_file='/fake/path')

    def test_init_client_auth_error(self):
        with patch('builtins.open', mock_open(read_data='token123')):
            with patch('src.adapters.vault.hvac.Client') as MockClient:
                client = MockClient.return_value
                client.is_authenticated.return_value = False

                with pytest.raises(VaultAuthenticationError):
                    VaultClient(addr='http://fake', token_file='/fake/token')

    def test_init_client_connection_error(self):
        with patch('src.adapters.vault.hvac.Client', side_effect=Exception('connection failed')):
            with patch('builtins.open', mock_open(read_data='token123')):
                with pytest.raises(VaultConnectionError):
                    VaultClient(addr='http://fake', token_file='/fake/path')
