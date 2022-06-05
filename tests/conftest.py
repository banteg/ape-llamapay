import pytest

from ape_llamapay import llamapay


@pytest.fixture(scope="session")
def factory():
    return llamapay.Factory()
