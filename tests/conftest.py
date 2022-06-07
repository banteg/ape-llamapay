import pytest

from ape_llamapay import llamapay


@pytest.fixture(scope="session")
def factory():
    return llamapay.Factory()


@pytest.fixture(scope="session")
def pool():
    return llamapay.Factory().get_pool("DAI")


@pytest.fixture(scope="session")
def ape(accounts):
    return accounts[0]


@pytest.fixture(scope="session")
def babe(accounts):
    return accounts[1]
