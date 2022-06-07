def test_stream_id(pool, stream):
    assert stream.id == pool.contract.getStreamId(stream.source, stream.target, stream.rate)


def test_stream_withdrawable(pool, stream_live):
    stream = stream_live
    withdrawable_amount = pool.contract.withdrawable(
        stream.source, stream.target, stream.rate
    ).withdrawableAmount
    assert stream.balance * pool.scale == withdrawable_amount


def test_stream_create(pool, stream, bird):
    receipt = stream.create(sender=bird)
    log = next(receipt.decode_logs(pool.contract.StreamCreated))
    assert log.amountPerSec == stream.rate


def test_stream_withdraw(pool, stream_live, bird):
    receipt = pool.withdraw(stream_live.source, stream_live.target, stream_live.rate, sender=bird)
    log = next(receipt.decode_logs(pool.token.Transfer))
    assert log.amount > 0


def test_stream_cancel(pool, bird, bee):
    rate = "100 DAI/month"
    pool.create_stream(bee, rate, sender=bird)
    receipt = pool.cancel_stream(bee, Rate.parse(rate).per_sec, sender=bird)
    log = next(receipt.decode_logs(pool.contract.StreamCancelled))


def test_stream_pause(pool, bird, bee):
    rate = "100 DAI/month"
    pool.create_stream(bee, rate, sender=bird)
    receipt = pool.pause_stream(bee, Rate.parse(rate).per_sec, sender=bird)
    log = next(receipt.decode_logs(pool.contract.StreamPaused))


def test_stream_replace(pool, bird, bee):
    rate = "100 DAI/month"
    pool.create_stream(bee, rate, sender=bird)
    receipt = pool.pause_stream(bee, Rate.parse(rate).per_sec, sender=bird)
    log = next(receipt.decode_logs(pool.contract.StreamPaused))

