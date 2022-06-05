from secrets import token_urlsafe

import pytest
from ape.exceptions import ConversionError
from ape_tokens import tokens

from ape_llamapay.llamapay import PoolNotDeployed


def test_factory_get_pool(factory):
    assert factory.get_pool(str(tokens["DAI"])) == factory.get_pool("DAI")


def test_factory_get_pool_not_address(factory):
    with pytest.raises(ConversionError):
        factory.get_pool(token_urlsafe(16))


def test_factory_get_pool_not_exists(factory):
    with pytest.raises(PoolNotDeployed):
        factory.get_pool("UST")  # too soon?


def test_create_pool(factory, accounts):
    pool = factory.create_pool("YFI", sender=accounts[0])
    assert pool.token == tokens["YFI"]
