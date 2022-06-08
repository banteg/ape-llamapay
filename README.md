# ape-llamapay

Manage [LlamaPay](https://llamapay.io) payment streams effortlessly from [Ape Framework](https://www.apeworx.io).

## Quick Usage

You can use this SDK in `ape console` or in ape scripts. A short example:

```python
from llamapay import Factory

factory = Factory()
factory.create_stream('banteg.eth', '1000 DAI/month', sender=accounts.load('dev'))
```

If deployment exists on the connected network, it will be automatically picked up.

A `Factory` is a registry and deployer of new pools. Each `Pool` manages all streams of a specific token. A `Stream` stores metadata like `source`, `target`, `rate` and allows operations on streams.

You can find pools by token address or symbol, courtesy of `ape-tokens`:
```python
factory.pools
factory.create_pool('YFI')
factory.get_pool('DAI')
```

You can find streams from event logs and filter them by `source` or `target`, including their ENS names, courtesy of `ape-ens`:
```python
pool.all_streams
pool.find_streams(source='ychad.eth')
pool.find_streams(target='wentokyo.eth')
```

To fund your streams you will need to deposit funds into a pool:
```python
pool.get_balance('ychad.eth')
# infinite approve (optional)
pool.approve(sender=dev)
# auto approves the requested amount
pool.deposit('1000 DAI', sender=dev)
# withdraw all
pool.withdraw(sender=dev)
# withdraw some
pool.withdraw(Decimal('500'), sender=dev)
```

Token amounts can be specified as `int` for wei, `Decimal` for tokens, or `str` to be converted by `ape-tokens` based on their decimals.

It is easiest to prepare a stream from the `Pool` instance:
```python
stream = pool.make_stream(source=dev, target=crush, rate='1000 DAI/month')
```

You can specify the rate as `int` for the internal 1e20 tokens per second representation or use a simple `str` format of `amount symbol/duration` like `1 YFI/week` or `200,000 UNI/year`.

Now that you have a `Stream` prepared, you can create it:
```python
stream.create(sender=dev)
stream.pause(sender=dev)
stream.cancel(sender=dev)
stream.replace(new_stream, sender=dev)
stream.modify(target=new_crush, sender=dev)
stream.modify(rate=stream.rate * 2, sender=dev)
# check your withdrawable balance
stream.balance
# push tokens to recipient or withdraw them if you are one (these methods are the same)
stream.send(sender=dev)
stream.withdraw(sender=dev)
```

## Dependencies

* [python3](https://www.python.org/downloads) version 3.7 or greater, python3-dev

## Installation

### via `pip`

You can install the latest release via [`pip`](https://pypi.org/project/pip/):

```bash
pip install llamapay
```

### via `setuptools`

You can clone the repository and use [`setuptools`](https://github.com/pypa/setuptools) for the most up-to-date version:

```bash
git clone https://github.com/banteg/ape-llamapay.git
cd ape-llamapay
python3 setup.py install
```

## Development

This project is in development and should be considered a beta.
Things might not be in their final state and breaking changes may occur.
Comments, questions, criticisms and pull requests are welcomed.

## License

This project is licensed under the [Apache 2.0](LICENSE).
