"""Entry point for running the Pantos Client CLI.

"""
import argparse
import decimal
import getpass
import importlib.resources
import pathlib
import shutil
import sys
import typing
import uuid

from pantos.client.library import api
from pantos.common.servicenodes import ServiceNodeTransferStatus

from pantos.cli.application import initialize_application
from pantos.cli.configuration import config
from pantos.cli.configuration import get_blockchain_config
from pantos.cli.exceptions import ClientCliError


def main() -> None:
    initialize_application()
    argument_parser = _create_argument_parser()
    arguments = argument_parser.parse_args()
    try:
        if arguments.command == 'balance':
            _execute_command_balance(arguments)
        elif arguments.command == 'bids':
            _execute_command_bids(arguments)
        elif arguments.command == 'transfer':
            _execute_command_transfer(arguments)
        elif arguments.command == 'status':
            _execute_command_status(arguments)
        elif arguments.command == 'create-config':
            _execute_command_create_config(arguments)
        else:
            raise NotImplementedError
    except Exception as error:
        if config['application']['debug']:
            raise
        print(error)
        sys.exit(1)


def _create_argument_parser() -> argparse.ArgumentParser:
    active_blockchain_names = sorted([
        blockchain.name.lower() for blockchain in api.Blockchain
        if get_blockchain_config(blockchain)['active']
    ])
    # Show help if no argument is given
    if len(sys.argv) == 1:
        sys.argv.append('--help')
    # Set up the argument parser
    parser = argparse.ArgumentParser(
        prog='pantos-client',
        description='Client for interacting with the Pantos multi-blockchain '
        'token system.')
    subparsers = parser.add_subparsers(dest='command')
    # Argument parser for showing an account balance
    parser_balance = subparsers.add_parser(
        'balance', help='show the balance of your accounts')
    parser_balance.add_argument(
        'blockchain', choices=active_blockchain_names,
        help='blockchain where your account is located')
    parser_balance.add_argument(
        'token', type=api.TokenSymbol,
        help='symbol of the Pantos-supported token to show the balance for')
    parser_balance.add_argument(
        '-k', '--keystore', type=pathlib.Path,
        help='path to a keystore file with your encrypted private key '
        '(default keystore is used if not provided)')
    # Argument parser for service node bids
    parser_bids = subparsers.add_parser(
        'bids', help='list the available service node bids')
    parser_bids.add_argument(
        'source', choices=active_blockchain_names,
        help='source blockchain (where you hold the tokens to be transferred)')
    parser_bids.add_argument(
        'destination', choices=active_blockchain_names,
        help='destination blockchain (where the recipient\'s account is '
        'located)')
    # Argument parser for transfers
    parser_transfer = subparsers.add_parser(
        'transfer', help='transfer tokens to another account (possibly on '
        'another blockchain)')
    parser_transfer.add_argument(
        'source', choices=active_blockchain_names,
        help='source blockchain (where you hold the tokens to be transferred)')
    parser_transfer.add_argument(
        'destination', choices=active_blockchain_names,
        help='destination blockchain (where the recipient\'s account is '
        'located)')
    parser_transfer.add_argument(
        'recipient', type=api.BlockchainAddress,
        help='address of the recipient on the destination blockchain')
    parser_transfer.add_argument(
        'token', type=api.TokenSymbol,
        help='symbol of the Pantos-supported token to be transferred')
    parser_transfer.add_argument(
        'amount', type=decimal.Decimal,
        help='amount of tokens to be transferred to the recipient')
    parser_transfer.add_argument(
        '-k', '--keystore', type=pathlib.Path,
        help='path to a keystore file with your encrypted private key '
        '(default keystore is used if not provided)')
    parser_transfer.add_argument(
        '-s', '--service', nargs=2, type=_string_int_pair,
        help='address and bid ID of the service node on the source blockchain '
        '(least expensive service node bid is used if not provided)',
        metavar=('node', 'bid'))
    parser_transfer.add_argument(
        '-y', '--yes', action='store_true',
        help='transfer the tokens immediately without prior confirmation')
    # Argument parser for status
    parser_status = subparsers.add_parser('status',
                                          help='show the status of a transfer')
    parser_status.add_argument('source', choices=active_blockchain_names,
                               help='the source blockchain of the transfer')
    parser_status.add_argument(
        'service', type=api.BlockchainAddress,
        help='the service node which processed the transfer')
    parser_status.add_argument(
        'task', type=uuid.UUID,
        help='task ID of the transfer to show the status for')
    parser_status.add_argument(
        '-b', '--blocks', type=int,
        help='The number of blocks to query for the transfer on the '
        'destination blockchain. If not specified, the query will '
        'include all blocks from the latest to the genesis block.')
    parser_config = subparsers.add_parser('create-config',
                                          help='Create a new empty env file')
    parser_config.add_argument(
        '-p', '--path', type=pathlib.Path, default=None,
        help='Path where to create the env file, defaults to the '
        'current working directory')
    return parser


_string_int_pair_first = True


def _string_int_pair(argument):
    global _string_int_pair_first
    if _string_int_pair_first:
        _string_int_pair_first = False
        assert isinstance(argument, str)
        return argument
    else:
        _string_int_pair_first = True
        try:
            return int(argument)
        except ValueError:
            raise argparse.ArgumentTypeError(
                f'invalid int value: \'{argument}\'')


def _execute_command_balance(arguments: argparse.Namespace) -> None:
    blockchain = api.Blockchain.from_name(arguments.blockchain)
    private_key = _load_private_key(blockchain, arguments.keystore)
    balance = api.retrieve_token_balance(blockchain, private_key,
                                         arguments.token)
    assert isinstance(balance, decimal.Decimal)
    _print_balance(blockchain, arguments.token, balance)


def _execute_command_bids(arguments: argparse.Namespace) -> None:
    source_blockchain = api.Blockchain.from_name(arguments.source)
    destination_blockchain = api.Blockchain.from_name(arguments.destination)
    service_node_bids = api.retrieve_service_node_bids(source_blockchain,
                                                       destination_blockchain)
    _print_bids(source_blockchain, destination_blockchain, service_node_bids)


def _execute_command_transfer(arguments: argparse.Namespace) -> None:
    source_blockchain = api.Blockchain.from_name(arguments.source)
    destination_blockchain = api.Blockchain.from_name(arguments.destination)
    if not arguments.yes:
        _print_transfer_inputs(
            source_blockchain, destination_blockchain, arguments.recipient,
            arguments.token, arguments.amount, arguments.keystore,
            None if arguments.service is None else arguments.service[0],
            None if arguments.service is None else arguments.service[1])
        execute = input('Are you sure you want to execute this transfer? '
                        '(no/yes, default: no) ')
        if execute != 'yes':
            print('\nTransfer aborted')
            return
    sender_private_key = _load_private_key(source_blockchain,
                                           arguments.keystore)
    service_node_task_info = api.transfer_tokens(
        source_blockchain, destination_blockchain, sender_private_key,
        arguments.recipient, arguments.token, arguments.amount,
        None if arguments.service is None else
        (arguments.service[0], arguments.service[1]))
    _print_transfer_output(service_node_task_info)


def _execute_command_status(arguments: argparse.Namespace) -> None:
    source_blockchain = api.Blockchain.from_name(arguments.source)
    service_node_address = arguments.service
    task_id = arguments.task
    blocks = arguments.blocks
    transfer_status = api.get_token_transfer_status(source_blockchain,
                                                    service_node_address,
                                                    task_id, blocks)
    _print_status(source_blockchain, service_node_address, task_id,
                  transfer_status)


def _execute_command_create_config(arguments: argparse.Namespace) -> None:
    path = arguments.path
    if path is None:
        path = pathlib.Path.cwd()

    path.mkdir(parents=True, exist_ok=True)

    # List and copy all .env files from the pantos resource directory
    resource_path = importlib.resources.files('pantos')
    for env_file in resource_path.iterdir():
        env_file_path = pathlib.Path(env_file.name)
        if env_file_path.suffix == '.env':
            shutil.copy(env_file_path, path / env_file_path.name)
    print(f'Created .env files in {path}')


def _load_private_key(
        blockchain: api.Blockchain,
        keystore_path: typing.Optional[pathlib.Path] = None) -> api.PrivateKey:
    keystore_config = get_blockchain_config(blockchain).get('keystore')
    if keystore_path is None:
        if keystore_config is None:
            raise ClientCliError(
                'the keystore must be given as an argument or must be added '
                f'to the {blockchain.name} configuration')
        keystore_path = pathlib.Path(keystore_config['file'])
    if not keystore_path.is_file():
        raise ClientCliError(f'the keystore {keystore_path} is not available')
    try:
        keystore = keystore_path.read_text()
    except Exception:
        raise ClientCliError(f'unable to read the keystore {keystore_path}')
    password = (None if keystore_config is None else
                keystore_config.get('password'))
    if password is None:
        password = getpass.getpass('Enter your keystore password: ')
    return api.decrypt_private_key(blockchain, keystore, password)


def _print_balance(blockchain: api.Blockchain, token_symbol: api.TokenSymbol,
                   balance: decimal.Decimal) -> None:
    print(
        f'Your {token_symbol.upper()} token balance on {blockchain.name}:\n'  # noqa E231
        f'{balance}')


def _print_bids(
        source_blockchain: api.Blockchain,
        destination_blockchain: api.Blockchain,
        service_node_bids: typing.Dict[api.BlockchainAddress,
                                       typing.List[api.ServiceNodeBid]]) \
        -> None:
    print('Pantos service node bids for token transfers from the\n'
          f'source blockchain {source_blockchain.name} to the destination '
          f'blockchain {destination_blockchain.name}:\n')  # noqa E231
    print('Service node\t\t\t\t\tBid ID\tTime\tFee')
    print('\t\t\t\t\t\t\t(s)\t(PAN)')
    print('==================================='
          '==================================')
    for service_node_address, bids in service_node_bids.items():
        for bid in bids:
            print(f'{service_node_address}\t{bid.execution_time}'
                  f'\t{bid.fee}')


def _print_transfer_inputs(source_blockchain: api.Blockchain,
                           destination_blockchain: api.Blockchain,
                           recipient_address: api.BlockchainAddress,
                           token_symbol: api.TokenSymbol,
                           amount: decimal.Decimal,
                           keystore_path: typing.Optional[pathlib.Path] = None,
                           service_node_address: typing.Optional[
                               api.BlockchainAddress] = None,
                           bid_id: typing.Optional[int] = None) -> None:
    print('New Pantos transfer:\n')
    print(f'Source blockchain:\t{source_blockchain.name}')  # noqa E231
    print(f'Destination blockchain:'  # noqa E231
          f'\t{destination_blockchain.name}')
    print(f'Recipient ({destination_blockchain.name}):'  # noqa E231
          f'\t{recipient_address}')
    print(f'Token symbol:\t\t{token_symbol.upper()}')  # noqa E231
    print(f'Amount:\t\t\t{amount}')  # noqa E231
    print(f'Keystore ({source_blockchain.name}):\t'  # noqa E231
          '{}'.format('default (from configuration)' if keystore_path is
                      None else keystore_path))
    print('Service node:\t\t{}'.format(
        'default (lowest fee)' if service_node_address is
        None else service_node_address))
    print('Service node bid:\t{}\n'.format('default (lowest fee)' if bid_id is
                                           None else bid_id))


def _print_transfer_output(
        service_node_task_info: api.ServiceNodeTaskInfo) -> None:
    print(f'\nThe service node {service_node_task_info.service_node_address}\n'
          'accepted the transfer request and returned\n'
          f'the following task ID: {service_node_task_info.task_id}')


def _print_status(source_blockchain: api.Blockchain,
                  service_node_address: api.BlockchainAddress,
                  task_id: uuid.UUID,
                  transfer_status: api.TokenTransferStatus) -> None:
    print('Transfer status:\n')
    print(f'Service node address:\t\t{service_node_address}')  # noqa E231
    print(f'Service node task ID:\t\t{task_id}\n')  # noqa E231
    print(f'Sender address:\t\t\t'  # noqa E231
          f'{transfer_status.sender_address}')
    print(f'Recipient address:\t\t'  # noqa E231
          f'{transfer_status.recipient_address}')
    print(f'Token amount:\t\t\t{transfer_status.amount}')  # noqa E231
    print(f'Source token address:\t\t'  # noqa E231
          f'{transfer_status.source_token_address}')
    print(f'Destination token address:\t'  # noqa E231
          f'{transfer_status.destination_token_address}\n')

    print(f'Source blockchain:\t\t{source_blockchain.name}')  # noqa E231
    print(f'Source transfer status:\t\t'  # noqa E231
          f'{transfer_status.source_transfer_status.name}')  # noqa E231
    if (transfer_status.source_transfer_status
            is ServiceNodeTransferStatus.CONFIRMED):
        print(f'Source transfer ID:\t\t'  # noqa E231
              f'{transfer_status.source_transfer_id}')
        print(f'Source transaction ID:\t\t'  # noqa E231
              f'{transfer_status.source_transaction_id}')
    print('')

    print(f'Destination blockchain:\t\t'  # noqa E231
          f'{transfer_status.destination_blockchain.name}')  # noqa E231
    print(f'Destination transfer status:\t'  # noqa E231
          f'{transfer_status.destination_transfer_status.name}')  # noqa E231
    if (transfer_status.destination_transfer_status
            is not api.DestinationTransferStatus.UNKNOWN):
        print(f'Destination transfer ID:\t'  # noqa E231
              f'{transfer_status.destination_transfer_id}')
        print(f'Destination transaction ID:\t'  # noqa E231
              f'{transfer_status.destination_transaction_id}')
        print(f'Validator nonce:\t\t'  # noqa E231
              f'{transfer_status.validator_nonce}')
        print(f'Signer addresses:\t\t'  # noqa E231
              f'{transfer_status.signer_addresses}')
        print(f'Signatures:\t\t\t{transfer_status.signatures}')  # noqa E231


if __name__ == '__main__':
    main()
