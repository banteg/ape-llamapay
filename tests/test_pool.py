from decimal import Decimal
import pytest
from ape_tokens.managers import ERC20

from llamapay.constants import DURATION_TO_SECONDS
from llamapay import Rate


### views


def test_pool_get_balance(pool):
    assert pool.get_balance("0xFEB4acf3df3cDEA7399794D0869ef76A6EfAff52") > 0


### actions


@pytest.mark.parametrize("amount", [10**21, "1000 DAI", Decimal("1000")])
def test_pool_approve(pool, token, bird, amount):
    wei_amount = 10**21
    pool.approve(amount, sender=bird)
    assert token.allowance(bird, pool.address) == wei_amount


def test_pool_approve_inf(pool, token, bird):
    pool.approve(sender=bird)
    max_uint = 2**256 - 1
    assert token.allowance(bird, pool.address) == max_uint


@pytest.mark.parametrize("amount", [10**21, "1000 DAI", Decimal("1000")])
def test_pool_deposit(pool, token, bird, amount):
    token_amount = Decimal("1000")
    # should approve automatically
    pool.deposit(amount, sender=bird)
    assert pool.get_balance(bird) == token_amount
    assert token.allowance(bird, pool.address) == 0


@pytest.mark.parametrize("amount", [10**21, "1000 DAI", Decimal("1000")])
def test_pool_withdraw(pool, bird, token, amount):
    amount = pool._convert_amount(amount)
    pool.deposit(amount, sender=bird)
    pool.withdraw(amount, sender=bird)
    assert pool.get_balance(str(bird)) == 0
    assert token.balanceOf(str(bird)) == 10**24


@pytest.mark.parametrize("amount", [10**21, "1000 DAI", Decimal("1000")])
def test_pool_withdraw_all(pool, bird, token, amount):
    pool.deposit(amount, sender=bird)
    pool.withdraw(sender=bird)
    assert token.balanceOf(str(bird)) == 10**24
    print(token.balanceOf(str(bird)))


def test_pool_create_stream():
    ...
