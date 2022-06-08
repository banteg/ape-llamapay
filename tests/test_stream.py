def test_stream_id(pool, stream):
    stream_id = pool.contract.getStreamId(stream.source, stream.target, stream.rate)
    assert stream.id == stream_id


def test_stream_create(pool, stream, bird):
    receipt = stream.create(sender=bird)
    log = next(receipt.decode_logs(pool.contract.StreamCreated))
    assert log.amountPerSec == stream.rate


def test_stream_withdrawable(pool, bird, bee, chain, token, stream):
    pool.deposit("1000 DAI", sender=bird)
    stream.create(sender=bird)
    chain.mine()
    assert stream.balance > 0

    result = pool.contract.withdrawable(stream.source, stream.target, stream.rate)
    assert stream.balance * pool.scale == result.withdrawableAmount


def test_stream_send(pool, stream, bird, bee, token, chain):
    pool.deposit("1000 DAI", sender=bird)
    stream.create(sender=bird)
    chain.mine()
    assert stream.balance > 0

    receipt = stream.withdraw(sender=bird)
    log = next(receipt.decode_logs(pool.token.Transfer))
    assert log.amount > 0


def test_stream_cancel(pool, stream, bird, bee):
    stream.create(sender=bird)
    receipt = stream.cancel(sender=bird)
    log = next(receipt.decode_logs(pool.contract.StreamCancelled))
    assert log.streamId == stream.id


def test_stream_pause(pool, stream, bird, bee):
    stream.create(sender=bird)
    receipt = stream.pause(sender=bird)
    log = next(receipt.decode_logs(pool.contract.StreamPaused))
    assert log.streamId == stream.id


def test_stream_replace(pool, bird, bee, stream):
    stream.create(sender=bird)
    new_stream = pool.make_stream(str(bird), str(bee), stream.rate * 2)
    receipt = stream.replace(new_stream, sender=bird)
    log = next(receipt.decode_logs(pool.contract.StreamModified))
    assert log.oldAmountPerSec * 2 == log.amountPerSec


def test_stream_modify(pool, bird, bee, stream):
    stream.create(sender=bird)
    receipt = stream.modify(rate=stream.rate * 2, sender=bird)
    log = next(receipt.decode_logs(pool.contract.StreamModified))
    assert log.oldAmountPerSec * 2 == log.amountPerSec
