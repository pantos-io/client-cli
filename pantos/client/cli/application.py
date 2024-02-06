"""Main Pantos Client CLI application module.

"""
import logging
import sys

from pantos.client.cli.configuration import load_config


def initialize_application() -> None:
    """Initialize the client CLI application.

    """
    logging.basicConfig(level=logging.WARNING)
    try:
        load_config()
    except Exception as error:
        print('unable to load the configuration: {}'.format(error))
        sys.exit(1)
