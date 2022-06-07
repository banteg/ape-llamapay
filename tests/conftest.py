import pytest

from llamapay import Factory, Pool, Stream


@pytest.fixture(scope="session")
def ape(accounts):
    return accounts[0]


@pytest.fixture(scope="session")
def babe(accounts):
    return accounts[1]


@pytest.fixture(scope="session")
def factory():
    return Factory()


@pytest.fixture(scope="session")
def pool(factory):
    return factory.get_pool("DAI")


@pytest.fixture(scope="session")
def stream(pool):
    return Stream(source=ape, target=babe, rate=1e20, pool=pool)
