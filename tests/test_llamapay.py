from secrets import token_urlsafe

import ape
import pytest
from ape.exceptions import ConversionError
from ape_tokens import tokens

from ape_llamapay.llamapay import PoolNotDeployed


def test_factory_get_pool(factory):
    assert factory.get_pool(tokens["DAI"].address) == factory.get_pool("DAI")


def test_factory_get_pool_not_address(factory):
    with pytest.raises(ConversionError):
        factory.get_pool(token_urlsafe(16))


def test_factory_get_pool_not_exists(factory):
    with pytest.raises(PoolNotDeployed) as e:
        factory.get_pool("UST")  # too soon


def test_create_pool(factory, accounts):
    pool = factory.create_pool("YFI", sender=accounts[0])
    print(pool)  # to hit the repr line
    assert pool.token == tokens["YFI"]


def test_create_pool_non_token(factory, accounts):
    with ape.reverts():
        factory.create_pool(str(accounts[1]), sender=accounts[0])
