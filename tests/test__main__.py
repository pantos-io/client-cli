import argparse
import decimal
import pathlib
import unittest
import unittest.mock
import uuid

import pytest
from pantos.client.library import api
from pantos.client.library.constants import TOKEN_SYMBOL_PAN
from pantos.common.blockchains.enums import Blockchain
from pantos.common.types import BlockchainAddress

from pantos.cli.__main__ import _load_private_key
from pantos.cli.__main__ import _string_int_pair
from pantos.cli.__main__ import main
from pantos.cli.exceptions import ClientCliError

TEST_KEYSTORE = pathlib.Path(__file__).parent.absolute() / "test.keystore"
MOCK_CLI_BLOCKCHAIN_COMMON_CONFIG = {
    'active': True,
    'keystore': {
        'file': 'test.keystore',
        'password': 'testing'  # NOSONAR
    }
}

MOCK_CLI_CONFIG_DICT = {
    "blockchains": {
        'avalanche': MOCK_CLI_BLOCKCHAIN_COMMON_CONFIG,
        'bnb_chain': MOCK_CLI_BLOCKCHAIN_COMMON_CONFIG,
        'celo': MOCK_CLI_BLOCKCHAIN_COMMON_CONFIG,
        'cronos': MOCK_CLI_BLOCKCHAIN_COMMON_CONFIG,
        'ethereum': MOCK_CLI_BLOCKCHAIN_COMMON_CONFIG,
        'polygon': MOCK_CLI_BLOCKCHAIN_COMMON_CONFIG,
        'fantom': {
            'active': False
        },
        'solana': {
            'active': False
        },
    }
}

MOCK_LIB_CONFIG_DICT = {
    "blockchains": {
        'avalanche': {
            'active': True,
            'provider': '',
            'average_block_time': 3,
            'confirmations': 20,
            'chain_id': 99999
        },
        'bnb_chain': {
            'active': True,
            'provider': '',
            'average_block_time': 3,
            'confirmations': 20,
            'chain_id': 99998
        },
        'celo': {
            'active': False
        },
        'cronos': {
            'active': False
        },
        'ethereum': {
            'active': True,
            'provider': '',
            'average_block_time': 3,
            'confirmations': 20,
            'chain_id': 99997
        },
        'fantom': {
            'active': False
        },
        'polygon': {
            'active': True,
            'provider': '',
            'average_block_time': 3,
            'confirmations': 20,
            'chain_id': 99996
        },
        'solana': {
            'active': False
        },
    }
}


@unittest.mock.patch('pantos.client.library.configuration.config')
@unittest.mock.patch('pantos.cli.configuration.config')
@unittest.mock.patch('pantos.client.library.api.retrieve_token_balance')
def test_balance(mock_retrieve_token_balance, mock_cli_config, mock_lib_config,
                 capsys):
    mock_retrieve_token_balance.return_value = decimal.Decimal('0.4')
    mock_cli_config.__getitem__.side_effect = MOCK_CLI_CONFIG_DICT.__getitem__
    mock_lib_config.__getitem__.side_effect = MOCK_LIB_CONFIG_DICT.__getitem__

    cmd = f'pantos.cli balance -k {TEST_KEYSTORE} bnb_chain pan'
    expected = 'Your PAN token balance on BNB_CHAIN:\n0.4\n'

    with unittest.mock.patch('sys.argv', cmd.split(' ')):
        main()

    mock_retrieve_token_balance.assert_called_once_with(
        Blockchain.BNB_CHAIN, unittest.mock.ANY, TOKEN_SYMBOL_PAN)

    captured = capsys.readouterr()
    assert captured.out == expected


@unittest.mock.patch('pantos.client.library.configuration.config')
@unittest.mock.patch('pantos.cli.configuration.config')
def test_not_implemented(mock_cli_config, mock_lib_config, capsys):
    mock_cli_config.__getitem__.side_effect = MOCK_CLI_CONFIG_DICT.__getitem__
    mock_lib_config.__getitem__.side_effect = MOCK_LIB_CONFIG_DICT.__getitem__

    cmd = 'pantos.cli status'
    with unittest.mock.patch('sys.argv',
                             cmd.split(' ')), pytest.raises(SystemExit):
        main()


@unittest.mock.patch('pantos.client.library.configuration.config')
@unittest.mock.patch('pantos.cli.configuration.config')
def test_no_arguments(mock_cli_config, mock_lib_config, capsys):
    mock_cli_config.__getitem__.side_effect = MOCK_CLI_CONFIG_DICT.__getitem__
    mock_lib_config.__getitem__.side_effect = MOCK_LIB_CONFIG_DICT.__getitem__

    cmd = 'pantos.cli'
    with unittest.mock.patch('sys.argv',
                             cmd.split(' ')), pytest.raises(SystemExit):
        main()


@unittest.mock.patch('pantos.client.library.configuration.config')
@unittest.mock.patch('pantos.cli.configuration.config')
@unittest.mock.patch('pantos.client.library.api.retrieve_token_balance')
def test_balance_blockchain_not_active(mock_retrieve_token_balance,
                                       mock_cli_config, mock_lib_config):
    mock_retrieve_token_balance.return_value = decimal.Decimal('0.4')
    mock_cli_config.__getitem__.side_effect = MOCK_CLI_CONFIG_DICT.__getitem__
    mock_lib_config.__getitem__.side_effect = MOCK_LIB_CONFIG_DICT.__getitem__

    cmd = f'pantos.cli balance -k {TEST_KEYSTORE} fantom pan'

    with unittest.mock.patch('sys.argv',
                             cmd.split(' ')), pytest.raises(SystemExit):
        main()

    assert not mock_retrieve_token_balance.called


@unittest.mock.patch('pantos.client.library.configuration.config')
@unittest.mock.patch('pantos.cli.configuration.config')
@unittest.mock.patch('pantos.client.library.api.retrieve_service_node_bids')
def test_bids(mock_retrieve_service_node_bids, mock_cli_config,
              mock_lib_config, capsys):
    mock_cli_config.__getitem__.side_effect = MOCK_CLI_CONFIG_DICT.__getitem__
    mock_lib_config.__getitem__.side_effect = MOCK_LIB_CONFIG_DICT.__getitem__

    bids = {
        '0x9C20a03E230e9733561E4bab598409bB6d5AED12': [
            api.ServiceNodeBid(source_blockchain=Blockchain.BNB_CHAIN,
                               destination_blockchain=Blockchain.ETHEREUM,
                               fee=decimal.Decimal('2'), execution_time=600,
                               valid_until=1701365269, signature='sig1'),
            api.ServiceNodeBid(source_blockchain=Blockchain.BNB_CHAIN,
                               destination_blockchain=Blockchain.ETHEREUM,
                               fee=decimal.Decimal('1.5'), execution_time=1200,
                               valid_until=1701365269, signature='sig12')
        ]
    }

    mock_retrieve_service_node_bids.return_value = bids

    cmd = "pantos.cli bids bnb_chain ethereum"
    expected = (
        'Pantos service node bids for token transfers from the\n'
        'source blockchain BNB_CHAIN to the destination blockchain ETHEREUM:\n'
        '\n'
        'Service node\t\t\t\t\tBid ID\tTime\tFee\n'
        '\t\t\t\t\t\t\t(s)\t(PAN)\n'
        '===================================================================='
        '=\n0x9C20a03E230e9733561E4bab598409bB6d5AED12\t600\t2\n'
        '0x9C20a03E230e9733561E4bab598409bB6d5AED12\t1200\t1.5\n')

    with unittest.mock.patch('sys.argv', cmd.split(' ')):
        main()

    mock_retrieve_service_node_bids.assert_called_once_with(
        Blockchain.BNB_CHAIN, Blockchain.ETHEREUM)

    captured = capsys.readouterr()
    assert captured.out == expected


@unittest.mock.patch('pantos.client.library.configuration.config')
@unittest.mock.patch('pantos.cli.configuration.config')
@unittest.mock.patch('pantos.client.library.api.retrieve_service_node_bids')
def test_bids_no_bids_available(mock_retrieve_service_node_bids,
                                mock_cli_config, mock_lib_config, capsys):
    mock_cli_config.__getitem__.side_effect = MOCK_CLI_CONFIG_DICT.__getitem__
    mock_lib_config.__getitem__.side_effect = MOCK_LIB_CONFIG_DICT.__getitem__
    bids = {'0x9C20a03E230e9733561E4bab598409bB6d5AED12': []}
    mock_retrieve_service_node_bids.return_value = bids

    cmd = "pantos.cli bids bnb_chain ethereum"
    expected = (
        'Pantos service node bids for token transfers from the\n'
        'source blockchain BNB_CHAIN to the destination blockchain ETHEREUM:\n'
        '\n'
        'Service node\t\t\t\t\tBid ID\tTime\tFee\n'
        '\t\t\t\t\t\t\t(s)\t(PAN)\n'
        '===================================================================='
        '=\n')

    with unittest.mock.patch('sys.argv', cmd.split(' ')):
        main()

    mock_retrieve_service_node_bids.assert_called_once_with(
        Blockchain.BNB_CHAIN, Blockchain.ETHEREUM)

    captured = capsys.readouterr()
    assert captured.out == expected


@unittest.mock.patch('pantos.client.library.configuration.config')
@unittest.mock.patch('pantos.cli.configuration.config')
@unittest.mock.patch('pantos.client.library.api.transfer_tokens')
def test_transfer(mock_transfer_tokens, mock_cli_config, mock_lib_config,
                  capsys):
    mock_cli_config.__getitem__.side_effect = MOCK_CLI_CONFIG_DICT.__getitem__
    mock_lib_config.__getitem__.side_effect = MOCK_LIB_CONFIG_DICT.__getitem__
    mock_transfer_tokens.return_value = uuid.UUID(
        '03ae67f4-ddf7-49d1-9355-99f8d3c256fb')

    cmd = (f'pantos.cli transfer -k {TEST_KEYSTORE} ethereum bnb_chain '
           "0x2003c848eB0201AA261892081fBC9E4FC559c494 pan .6 --yes")
    expected = (
        '\nThe service node accepted the transfer request and returned\n'
        'the following task ID: '
        '03ae67f4-ddf7-49d1-9355-99f8d3c256fb\n')

    with unittest.mock.patch('sys.argv', cmd.split(' ')):
        main()

    mock_transfer_tokens.assert_called_once_with(
        Blockchain.ETHEREUM, Blockchain.BNB_CHAIN, unittest.mock.ANY,
        BlockchainAddress('0x2003c848eB0201AA261892081fBC9E4FC559c494'),
        TOKEN_SYMBOL_PAN, decimal.Decimal('.6'), None)

    captured = capsys.readouterr()
    assert captured.out == expected


@unittest.mock.patch('pantos.cli.__main__.get_blockchain_config')
def test_load_private_key_no_private_key_no_config(mock_get_blockchain_config):
    mock_get_blockchain_config.return_value = {'ETHEREUM': None}
    with pytest.raises(ClientCliError):
        _load_private_key(api.Blockchain.ETHEREUM)


@unittest.mock.patch('pantos.client.library.configuration.config')
@unittest.mock.patch('pantos.cli.configuration.config')
def test_load_private_key_no_private_key(
    mock_cli_config,
    mock_lib_config,
):
    mock_cli_config.__getitem__.side_effect = MOCK_CLI_CONFIG_DICT.__getitem__
    mock_lib_config.__getitem__.side_effect = MOCK_LIB_CONFIG_DICT.__getitem__
    with pytest.raises(ClientCliError):
        _load_private_key(api.Blockchain.ETHEREUM)


@unittest.mock.patch('pantos.client.library.configuration.config')
@unittest.mock.patch('pantos.cli.configuration.config')
def test_load_private_key_no_keystore_file(mock_cli_config, mock_lib_config):
    mock_cli_config.__getitem__.side_effect = MOCK_CLI_CONFIG_DICT.__getitem__
    mock_lib_config.__getitem__.side_effect = MOCK_LIB_CONFIG_DICT.__getitem__

    with pytest.raises(ClientCliError):
        _load_private_key(api.Blockchain.ETHEREUM, pathlib.Path('test'))


def test_string_int_pair_correct():
    argument = "key=value"
    assert _string_int_pair(argument) == argument


@unittest.mock.patch('pantos.cli.__main__._string_int_pair_first', False)
def test_string_int_pair_value_error():
    argument = "key=value"
    with pytest.raises(argparse.ArgumentTypeError):
        _string_int_pair(argument)


@unittest.mock.patch('pantos.cli.__main__._string_int_pair_first', False)
def test_string_int_pair_correct_cast():
    argument = "1"
    assert _string_int_pair(argument) == int(argument)


if __name__ == '__main__':
    unittest.main()
