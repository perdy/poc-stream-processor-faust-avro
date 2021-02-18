import os
import typing

import hvac


class VaultError(Exception):
    pass


class VaultClient:
    def __init__(self, url: str):
        self.url = url

    def _get_token(
        self, environment_variable: typing.Optional[str] = None, file_path: typing.Optional[str] = None
    ) -> str:
        if environment_variable is None and file_path is None:
            raise ValueError("Either environment_variable or file_path should be provided")

        if environment_variable is not None:
            try:
                return os.environ[environment_variable]
            except KeyError:
                raise VaultError(f"Vault token not found in environment variable '{environment_variable}'")

        if file_path is not None:
            try:
                with open(file_path) as f:
                    return f.readline()
            except FileNotFoundError:
                raise VaultError(f'Vault token not found in file "{file_path}"')

    @property
    def client(self):
        if not hasattr(self, "_client"):
            raise VaultError("Vault client is not initialized")

        return self._client

    def secrets(self, path: str):
        try:
            vault_response = self.client.read(path)
            return vault_response["data"]
        except KeyError:
            raise VaultError(f'Wrong response from Vault "{vault_response}"')


class VaultClientAppID(VaultClient):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.app_id = self._get_token(
            environment_variable="VAULT_APP_ID",
            file_path=os.path.realpath(os.path.join(__file__, "..", "..", "appid")),
        )
        self.user_id = self._get_token(
            environment_variable="VAULT_USER_ID",
            file_path=os.path.realpath(os.path.join(__file__, "..", "..", "userid")),
        )

    def __enter__(self) -> "VaultClientAppID":
        self._client = hvac.Client(url=self.url)
        self._client.auth_app_id(app_id=self.app_id, user_id=self.user_id)
        if not self._client.is_authenticated():
            raise VaultError("Vault authentication error")

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        del self._client


class VaultMixin:
    """
    Clinner application's mixin that provides an easy way to inject environment variables from Vault.

    Following environment variables are required:
    - VAULT_URL
    - VAULT_NAMESPACE
    - VAULT_APP

    Authentication is based on Vault's AppID method so both app id and user id must be provided through environment
    variables named VAULT_APP_ID and VAULT_USER_ID or adding files named appid and userid in root directory.

    Blacklist and whitelist mechanism provides flexibility to avoid connecting vault in different environments.
    """

    VAULT_ENVIRONMENTS_BLACKLIST = ["local", "development"]
    VAULT_ENVIRONMENTS_WHITELIST = []

    def inject_vault_variables(self):
        if (
            self.args.environment in self.VAULT_ENVIRONMENTS_WHITELIST
            or self.args.environment not in self.VAULT_ENVIRONMENTS_BLACKLIST
        ):
            self.cli.logger.info("Injecting vault data for %s", self.args.environment)
            try:
                url = os.environ["VAULT_URL"]
                path = f"secret/{self.args.environment}/{os.environ['VAULT_NAMESPACE']}/{os.environ['VAULT_APP']}"
                with VaultClientAppID(url=url) as client:
                    secrets = client.secrets(path=path)
                    os.environ.update(secrets)
                    self.cli.logger.info("Variables injected from Vault: %s", ", ".join(secrets.keys()))
            except KeyError as e:
                raise VaultError(f"Variable {str(e)} not found")
