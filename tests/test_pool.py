import pytest
from ape_llamapay.llamapay import Rate, Stream
from hexbytes import HexBytes
from ape_llamapay.constants import DURATION_TO_SECONDS
from ape_tokens.managers import ERC20

# sample stream from here
# https://ethtx.info/mainnet/0x7979a77ab8a30bc6cd12e1df92e5ba0478a8907caf6e100317b7968668d0d4a2/
stream = Stream(
    payer="0xFEB4acf3df3cDEA7399794D0869ef76A6EfAff52",
    receiver="0x908dcdb61189b56f5cb7b0c60d332e3ee18d9300",
    rate_per_sec=192901234567901234,
)
stream_id = HexBytes("0xd634cf4ed24cbb7ce73d0764bcd0067c7d31f9143836ce431fe8c85e6f76263a")


def test_stream_id(pool):
    assert stream_id == pool.contract.getStreamId(stream.payer, stream.receiver, stream.rate)
    assert stream_id == stream.stream_id


def test_get_balance(pool):
    balance = pool.get_balance("0xFEB4acf3df3cDEA7399794D0869ef76A6EfAff52")
    print(balance)


def test_stream_withdrawable(pool):
    withdrawable = pool.get_withdrawable_amount(stream.payer, stream.receiver, stream.rate_per_sec)
    assert withdrawable > 0


def test_duration():
    # https://github.com/LlamaPay/interface/blob/main/utils/constants.ts#L282
    assert DURATION_TO_SECONDS["day"] == 86_400
    assert DURATION_TO_SECONDS["week"] == 604_800
    assert DURATION_TO_SECONDS["month"] == 2_592_000
    assert DURATION_TO_SECONDS["year"] == 31_104_000


@pytest.mark.parametrize(
    "rate",
    [
        "1000000/year",
        "100,000 UNI/day",
        "10_000 USDC/month",
        "10 YFI/year",
    ],
)
def test_rate(rate):
    r = Rate.parse(rate)
    print(r)
    print(repr(r))


### actions


def test_create_stream(pool, accounts):
    rate = "100 DAI/month"
    receipt = pool.create_stream(accounts[1], rate, sender=accounts[0])
    log = next(receipt.decode_logs(pool.contract.StreamCreated))
    assert log.amountPerSec == Rate.parse(rate).per_sec


def test_stream_withdraw(pool, accounts):
    receipt = pool.withdraw(stream.payer, stream.receiver, stream.rate_per_sec, sender=accounts[0])
    log = next(receipt.decode_logs(ERC20.events["Transfer"]))
    assert log.amount > 0


def test_stream_cancel(pool, accounts):
    rate = "100 DAI/month"
    pool.create_stream(accounts[1], rate, sender=accounts[0])
    receipt = pool.cancel_stream(accounts[1], Rate.parse(rate).per_sec, sender=accounts[0])
    log = next(receipt.decode_logs(pool.contract.StreamCancelled))


def test_stream_pause(pool, accounts):
    rate = "100 DAI/month"
    pool.create_stream(accounts[1], rate, sender=accounts[0])
    receipt = pool.pause_stream(accounts[1], Rate.parse(rate).per_sec, sender=accounts[0])
    log = next(receipt.decode_logs(pool.contract.StreamPaused))
