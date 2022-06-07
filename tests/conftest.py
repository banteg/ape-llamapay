import pytest

from llamapay import Factory, Stream


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
