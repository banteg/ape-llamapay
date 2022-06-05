from attr import Factory
import pytest
from ape.utils.testing import generate_dev_accounts
from ape_llamapay import llamapay


@pytest.fixture(scope="session")
def users():
    return generate_dev_accounts(
        hd_path_format="m/44'/60'/0'/0/{}",
    )


@pytest.fixture(scope="session")
def factory():
    return llamapay.Factory()
