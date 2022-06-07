import pytest
from ape import chain
from eth_abi import encode_abi
from eth_utils import keccak

from llamapay import Factory, Stream


def set_balance(token, account, value, storage_index):
    # obtain a token balance with this one simple trick
    slot = keccak(
        encode_abi(
            ["address", "uint"],
            [account, storage_index],
        )
    )
    chain.provider._make_request(
        "anvil_setStorageAt",
        [token, slot.hex(), hex(value)],
    )


@pytest.fixture(scope="session")
def bird(accounts):
    return accounts[0]


@pytest.fixture(scope="session")
def bee(accounts):
    return accounts[1]


@pytest.fixture(scope="session")
def factory():
    return Factory()


@pytest.fixture(scope="session")
def pool(factory):
    return factory.get_pool("DAI")


@pytest.fixture(scope="session")
def stream(pool, bird, bee):
    # stream 0.01 DAI per second from bird to bee
    return Stream(source=str(bird), target=str(bee), rate=10**18, pool=pool)


@pytest.fixture(scope="session")
def token(pool, bird):
    set_balance(str(pool.token), str(bird), 10**24, storage_index=2)
    return pool.token

