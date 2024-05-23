"""Main Pantos Client CLI application module.

"""
import logging
import sys

from pantos.cli.configuration import load_config


def initialize_application() -> None:
    """Intialize the client CLI application.

    """
    logging.basicConfig(level=logging.WARNING)
    try:
        load_config()
    except Exception as error:
        print('unable to load the configuration: {}'.format(error))
        sys.exit(1)
