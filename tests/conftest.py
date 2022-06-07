import pytest

from ape_llamapay import llamapay


@pytest.fixture(scope="session")
def factory():
    return llamapay.Factory()


@pytest.fixture(scope="session")
def pool():
    return llamapay.Factory().get_pool("DAI")
