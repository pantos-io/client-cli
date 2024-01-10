"""Common exceptions for the Pantos Client CLI.

"""
from pantos.client.library.exceptions import ClientError


class ClientCliError(ClientError):
    """Base exception class for all Pantos client CLI errors.

    """
    pass
