"""Shared fixtures for all pantos.cli package tests.

"""
import uuid

import hexbytes
import pytest
from pantos.client.library.api import TokenTransferStatus
from pantos.common.entities import BlockchainAddress

_SERVICE_NODE = BlockchainAddress('0x5188287E724140aa3C432dCfE69E00992aF09d09')

_TASK_UUID = uuid.UUID('b6b59888-41c2-4555-825f-47ce387d6853')

_TRANSACTION_HASH = hexbytes.HexBytes(
    '3273482cfbf640bd5a7056fc3fd418275d2537bb49638035e19f2c4ebcf2e3d9')

_SOURCE_TRANSFER_ID = 2

_DESTINATION_TRANSFER_ID = 3

_SENDER = BlockchainAddress('0x4958c0CdDb1649e8da454657733BA7AeC7069765')

_RECIPIENT = BlockchainAddress('0xDc825BC1Af2d4c02E9e2d03fF3b492A09d168124')

_SOURCE_TOKEN = BlockchainAddress('0x57FeAEC5F8f3A19264d8DfF24a88dA9F774e30a2')

_DESTINATION_TOKEN = BlockchainAddress(
    '0x49716ea49473c8B1164d2F503e50319D629CFFC6')

_AMOUNT = 100

_NONCE = 11111

_SIGNER_ADDRESSES = [
    BlockchainAddress('0xBb608811Bfc5fc3444863BC589C7e5F50DF1936a')
]

_SIGNATURES = [
    hexbytes.HexBytes(
        '665b95365f0724784d5c2792ca870ff4bf08b06590ac068f6f89ae7edf640bdd3'
        'aaa116b69b2e0927a3151de498f5f0131beafbadb6c12c1756baa532d931fa81c')
]


@pytest.fixture(scope='module')
def service_node():
    return _SERVICE_NODE


@pytest.fixture(scope='module')
def task_uuid():
    return _TASK_UUID


@pytest.fixture(scope='module')
def source_transaction_id():
    return _TRANSACTION_HASH


@pytest.fixture(scope='module')
def transaction_hash():
    return _TRANSACTION_HASH


@pytest.fixture(scope='module')
def source_transfer_id():
    return _SOURCE_TRANSFER_ID


@pytest.fixture(scope='module')
def destination_transfer_id():
    return _DESTINATION_TRANSFER_ID


@pytest.fixture(scope='module')
def sender():
    return _SENDER


@pytest.fixture(scope='module')
def recipient():
    return _RECIPIENT


@pytest.fixture(scope='module')
def source_token():
    return _SOURCE_TOKEN


@pytest.fixture(scope='module')
def destination_token():
    return _DESTINATION_TOKEN


@pytest.fixture(scope='module')
def amount():
    return _AMOUNT


@pytest.fixture(scope='module')
def nonce():
    return _NONCE


@pytest.fixture(scope='module')
def signer_addresses():
    return _SIGNER_ADDRESSES


@pytest.fixture(scope='module')
def signatures():
    return _SIGNATURES


@pytest.fixture(scope='function')
def token_transfer_status(request):
    return TokenTransferStatus(request.param[0], request.param[1],
                               request.param[2], _TRANSACTION_HASH.hex(),
                               _TRANSACTION_HASH.hex(), _SOURCE_TRANSFER_ID,
                               _DESTINATION_TRANSFER_ID, _SENDER, _RECIPIENT,
                               _SOURCE_TOKEN, _DESTINATION_TOKEN, _AMOUNT,
                               _NONCE, _SIGNER_ADDRESSES,
                               [signature.hex() for signature in _SIGNATURES])
