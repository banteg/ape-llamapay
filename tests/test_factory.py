import ape
import pytest
from ape.exceptions import ConversionError
from ape_tokens import tokens

from llamapay.exceptions import PoolNotDeployed


def test_factory_get_pool(factory):
    assert factory.get_pool(tokens["DAI"].address) == factory.get_pool("DAI")


def test_factory_get_pool_not_address(factory):
    with pytest.raises(ConversionError):
        factory.get_pool("not_an_address")


def test_factory_get_pool_not_exists(factory):
    with pytest.raises(PoolNotDeployed):
        factory.get_pool("UST")  # too soon


def test_create_pool(factory, bird):
    pool = factory.create_pool("YFI", sender=bird)
    assert pool.token == tokens["YFI"]


def test_create_pool_non_token(factory, bird, bee):
    non_token = str(bee)
    with ape.reverts():
        factory.create_pool(non_token, sender=bird)


def test_pools(factory):
    assert len(factory.pools) >= 1
