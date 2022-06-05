from secrets import token_urlsafe

import pytest
from ape.exceptions import ConversionError
from ape_tokens import tokens

from ape_llamapay.llamapay import PoolNotDeployed


def test_factory_get_pool(factory):
    dai = tokens["DAI"].address
    assert factory.get_pool(dai) == factory.get_pool("DAI")


def test_factory_get_pool_not_address(factory, users):
    with pytest.raises(ConversionError):
        factory.get_pool(token_urlsafe(16))


def test_factory_get_pool_not_exists(factory, users):
    with pytest.raises(PoolNotDeployed):
        factory.get_pool("UST")  # too soon?
