"""Module for loading, validating, and accessing the Client CLI's
configuration.

"""
import itertools
import typing

from pantos.common.blockchains.base import Blockchain
from pantos.common.configuration import Config

_DEFAULT_FILE_NAME: typing.Final[str] = 'pantos-client-cli.conf'
"""Default configuration file name."""

config = Config(_DEFAULT_FILE_NAME)
"""Singleton object holding the configuration values."""

_VALIDATION_SCHEMA_BLOCKCHAIN = {
    'type': 'dict',
    'schema': {
        'active': {
            'type': 'boolean',
            'default': True
        },
        'keystore': {
            'type': 'dict',
            'schema': {
                'file': {
                    'type': 'string',
                    'required': True,
                    'empty': False
                },
                'password': {
                    'type': 'string',
                    'empty': False
                }
            }
        }
    }
}
"""Schema for validating a blockchain entry in the configuration file."""

_VALIDATION_SCHEMA = {
    'application': {
        'type': 'dict',
        'schema': {
            'debug': {
                'type': 'boolean',
                'default': False
            }
        }
    },
    'blockchains': {
        'type': 'dict',
        'schema': dict(
            zip([b.name.lower() for b in Blockchain],
                itertools.repeat(_VALIDATION_SCHEMA_BLOCKCHAIN)))
    }
}
"""Schema for validating the configuration file."""


def get_blockchain_config(
        blockchain: Blockchain) -> typing.Dict[str, typing.Any]:
    """Get a blockchain-specific configuration dictionary.

    Parameters
    ----------
    blockchain : Blockchain
        The blockchain to get the configuration for.

    Returns
    -------
    dict
        The blockchain-specific configuration.

    """
    return config['blockchains'][blockchain.name.lower()]


def load_config(file_path: typing.Optional[str] = None,
                reload: bool = True) -> None:
    """Load the configuration from a configuration file.

    Parameters
    ----------
    file_path : str or None
        The path to the configuration file (typical configuration file
        locations are searched if none is specified).
    reload : bool
        If True, the configuration is also loaded if it was already
        loaded before.

    Raises
    ------
    pantos.common.configuration.ConfigError
        If the configuration cannot be loaded (e.g. due to an invalid
        configuration file).

    See Also
    --------
    Config.load

    """
    if reload or not config.is_loaded():
        config.load(_VALIDATION_SCHEMA, file_path)
