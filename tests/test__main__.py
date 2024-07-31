import argparse
import decimal
import itertools
import pathlib
import unittest
import unittest.mock

import pytest
from pantos.client.library import api
from pantos.client.library.api import DestinationTransferStatus
from pantos.client.library.api import ServiceNodeTaskInfo
from pantos.client.library.constants import TOKEN_SYMBOL_PAN
from pantos.common.blockchains.enums import Blockchain
from pantos.common.entities import ServiceNodeTransferStatus
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


@unittest.mock.patch('shutil.copy')
@unittest.mock.patch('pathlib.Path.mkdir')
@unittest.mock.patch('pantos.client.library.configuration.config')
@unittest.mock.patch('pantos.cli.configuration.config')
def test_config_create(mock_cli_config, mock_lib_config, mock_mkdir,
                       mock_shutil_copy: unittest.mock.MagicMock, capsys):
    mock_cli_config.__getitem__.side_effect = MOCK_CLI_CONFIG_DICT.__getitem__
    mock_lib_config.__getitem__.side_effect = MOCK_LIB_CONFIG_DICT.__getitem__

    cmd = 'pantos.cli create-config'

    with unittest.mock.patch('sys.argv', cmd.split(' ')):
        main()

    mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)

    mock_shutil_copy.assert_has_calls([
        unittest.mock.call(pathlib.Path('client-cli.env'),
                           pathlib.Path.cwd() / 'client-cli.env'),
        unittest.mock.call(pathlib.Path('client-library.env'),
                           pathlib.Path.cwd() / 'client-library.env')
    ], any_order=True)  # required because 3.12 changed the order

    captured = capsys.readouterr()
    assert captured.out == f'Created .env files in {pathlib.Path.cwd()}\n'


@unittest.mock.patch('shutil.copy')
@unittest.mock.patch('pathlib.Path.mkdir')
@unittest.mock.patch('pantos.client.library.configuration.config')
@unittest.mock.patch('pantos.cli.configuration.config')
def test_config_create_custom_dir(mock_cli_config, mock_lib_config, mock_mkdir,
                                  mock_shutil_copy: unittest.mock.MagicMock,
                                  capsys):
    mock_cli_config.__getitem__.side_effect = MOCK_CLI_CONFIG_DICT.__getitem__
    mock_lib_config.__getitem__.side_effect = MOCK_LIB_CONFIG_DICT.__getitem__

    cmd = 'pantos.cli create-config -p /foo'

    with unittest.mock.patch('sys.argv', cmd.split(' ')):
        main()

    mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)

    mock_shutil_copy.assert_has_calls([
        unittest.mock.call(pathlib.Path('client-cli.env'),
                           pathlib.Path('/foo/client-cli.env')),
        unittest.mock.call(pathlib.Path('client-library.env'),
                           pathlib.Path('/foo/client-library.env'))
    ], any_order=True)  # required because 3.12 changed the order

    captured = capsys.readouterr()
    assert captured.out == 'Created .env files in /foo\n'


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
        'Service node\t\t\t\t\tTime\tFee\n'
        '\t\t\t\t\t\t(s)\t(PAN)\n'
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
        'Service node\t\t\t\t\tTime\tFee\n'
        '\t\t\t\t\t\t(s)\t(PAN)\n'
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
                  service_node, task_uuid, capsys):
    mock_cli_config.__getitem__.side_effect = MOCK_CLI_CONFIG_DICT.__getitem__
    mock_lib_config.__getitem__.side_effect = MOCK_LIB_CONFIG_DICT.__getitem__
    mock_transfer_tokens.return_value = ServiceNodeTaskInfo(
        task_uuid, service_node)

    cmd = (f'pantos.cli transfer -k {TEST_KEYSTORE} ethereum bnb_chain '
           "0x2003c848eB0201AA261892081fBC9E4FC559c494 pan .6 --yes")
    expected = (f'\nThe service node {service_node}\naccepted the transfer'
                f' request and returned\nthe following task ID: {task_uuid}\n')

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
def test_load_private_key_no_private_key(mock_cli_config, mock_lib_config):
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


@pytest.mark.parametrize('token_transfer_status', [
    list(tuple_) for tuple_ in itertools.product(
        Blockchain, ServiceNodeTransferStatus, DestinationTransferStatus)
], indirect=True)
@unittest.mock.patch('pantos.client.library.configuration.config')
@unittest.mock.patch('pantos.cli.configuration.config')
@unittest.mock.patch('pantos.client.library.api.get_token_transfer_status')
def test_print_status(mock_get_token_transfer_status, mock_cli_config,
                      mock_lib_config, token_transfer_status, service_node,
                      task_uuid, capsys):
    mock_cli_config.__getitem__.side_effect = MOCK_CLI_CONFIG_DICT.__getitem__
    mock_lib_config.__getitem__.side_effect = MOCK_LIB_CONFIG_DICT.__getitem__

    cmd = f'pantos.cli status ethereum {service_node} {task_uuid}'
    mock_get_token_transfer_status.return_value = token_transfer_status

    with unittest.mock.patch('sys.argv', cmd.split(' ')):
        main()
    captured = capsys.readouterr()

    _test_status_output(service_node, task_uuid, token_transfer_status,
                        captured.out)


def _test_status_output(service_node_address, service_node_task_uuid,
                        transfer_status, captured_output):
    expected_output = (
        'Transfer status:\n\n'
        f'Service node address:\t\t{service_node_address}\n'  # noqa E231
        f'Service node task ID:\t\t{service_node_task_uuid}\n\n'  # noqa E231
        f'Sender address:\t\t\t{transfer_status.sender_address}\n'  # noqa E231
        f'Recipient address:\t\t{transfer_status.recipient_address}\n'  # noqa E231
        f'Token amount:\t\t\t{transfer_status.amount}\n'  # noqa E231
        f'Source token address:\t\t{transfer_status.source_token_address}\n'  # noqa E231
        'Destination token address:\t'  # noqa E231
        f'{transfer_status.destination_token_address}\n\n'
        f'Source blockchain:\t\tETHEREUM\n'  # noqa E231
        'Source transfer status:\t\t'  # noqa E231
        f'{transfer_status.source_transfer_status.name}')
    if (transfer_status.source_transfer_status
            is ServiceNodeTransferStatus.CONFIRMED):
        expected_output += (
            f'\nSource transfer ID:\t\t{transfer_status.source_transfer_id}\n'  # noqa E231
            'Source transaction ID:\t\t'  # noqa E231
            f'{transfer_status.source_transaction_id}')
    expected_output += (
        '\n\nDestination blockchain:\t\t'  # noqa E231
        f'{transfer_status.destination_blockchain.name}\n'
        'Destination transfer status:\t'  # noqa E231
        f'{transfer_status.destination_transfer_status.name}\n')
    if (transfer_status.destination_transfer_status
            is not api.DestinationTransferStatus.UNKNOWN):
        expected_output += (
            f'Destination transfer ID:\t'  # noqa E231
            f'{transfer_status.destination_transfer_id}\n'
            'Destination transaction ID:\t'  # noqa E231
            f'{transfer_status.destination_transaction_id}\n'
            f'Validator nonce:\t\t{transfer_status.validator_nonce}\n'  # noqa E231
            f'Signer addresses:\t\t{transfer_status.signer_addresses}\n'  # noqa E231
            f'Signatures:\t\t\t{transfer_status.signatures}\n')  # noqa E231

    assert captured_output == expected_output


if __name__ == '__main__':
    unittest.main()
