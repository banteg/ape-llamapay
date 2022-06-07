from ape_llamapay.llamapay import Stream
from hexbytes import HexBytes
from ape_llamapay.constants import DURATION_TO_SECONDS

def test_stream_id(pool):
    # sample stream from here
    # https://ethtx.info/mainnet/0x7979a77ab8a30bc6cd12e1df92e5ba0478a8907caf6e100317b7968668d0d4a2/
    stream = Stream(
        sender="0xFEB4acf3df3cDEA7399794D0869ef76A6EfAff52",
        receiver="0x908dcdb61189b56f5cb7b0c60d332e3ee18d9300",
        rate=192901234567901234,
    )
    stream_id = HexBytes("0xd634cf4ed24cbb7ce73d0764bcd0067c7d31f9143836ce431fe8c85e6f76263a")
    assert stream_id == pool.contract.getStreamId(stream.sender, stream.receiver, stream.rate)
    assert stream_id == stream.stream_id


def test_get_balance(pool):
    balance = pool.get_balance("0xFEB4acf3df3cDEA7399794D0869ef76A6EfAff52")
    print(balance)


def test_duration():
    # https://github.com/LlamaPay/interface/blob/main/utils/constants.ts#L282
    assert DURATION_TO_SECONDS['day'] == 86_400
    assert DURATION_TO_SECONDS['week'] == 604_800
    assert DURATION_TO_SECONDS['month'] == 2_592_000
    assert DURATION_TO_SECONDS['year'] == 31_104_000


