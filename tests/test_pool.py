from decimal import Decimal

import pytest


def test_pool_get_balance(pool):
    assert pool.get_balance("0xFEB4acf3df3cDEA7399794D0869ef76A6EfAff52") > 0


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


def test_pool_create_stream(pool, bird, bee):
    stream = pool.make_stream(bird, bee, "1000 DAI/month")
    receipt = stream.create(sender=bird)
    log = next(receipt.decode_logs(pool.contract.StreamCreated))
    assert stream.rate == log.amountPerSec


def test_factory_create_stream(factory, bird, bee):
    stream = factory.create_stream(bee, "1000 DAI/month", sender=bird)
    print(stream)
