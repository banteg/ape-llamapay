from decimal import Decimal
from functools import cached_property
from typing import List, Literal, Optional, Union

from ape.types import AddressType
from ape.utils import ManagerAccessMixin
from ape_tokens import tokens
from ape_tokens.managers import ERC20
from eth_abi.packed import encode_abi_packed
from eth_utils import keccak
from pydantic import BaseModel
from ape.api import ReceiptAPI

from ape_llamapay.constants import (
    CONTRACT_TYPES,
    DURATION_TO_SECONDS,
    FACTORY_DEPLOYMENTS,
    PRECISION,
)


class PoolNotDeployed(Exception):
    pass


class Factory(ManagerAccessMixin):
    """
    LlamaPay streams for each token are contained in pools.
    This factory helps discover and deploy new pools.
    """

    def __init__(self):
        self.deployment = FACTORY_DEPLOYMENTS.get(
            ecosystem=self.provider.network.ecosystem.name,
            network=self.provider.network.name.replace("-fork", ""),
        )
        self.contract = self.create_contract(
            self.deployment.address, CONTRACT_TYPES["LlamaPayFactory"]
        )

    def get_pool(self, token: str) -> "Pool":
        """
        Get pool by token address or symbol.
        """
        token = self._resolve_token(token)
        address, is_deployed = self.contract.getLlamaPayContractByToken(token)
        if not is_deployed:
            raise PoolNotDeployed("deterministic address: %s" % address)

        return Pool(address, factory=self)

    def create_pool(self, token: str, **tx_args) -> "Pool":
        """
        Create a pool for a token and return it.
        """
        token = self._resolve_token(token)
        self.contract.createLlamaPayContract(token, **tx_args)

        return self.get_pool(token)

    @property
    def pools(self) -> List["Pool"]:
        """
        Get all pools deployed by a factory.
        """
        # TODO update to use multicall
        pool_count = self.contract.getLlamaPayContractCount()
        pools = [
            Pool(self.contract.getLlamaPayContractByIndex(i), factory=self)
            for i in range(pool_count)
        ]
        return pools

    def _resolve_token(self, token: str) -> AddressType:
        """
        Resolve token address by symbol, address or ENS.
        """
        try:
            token = tokens[token].address
        except KeyError:
            pass

        return self.conversion_manager.convert(token, AddressType)


class Pool(ManagerAccessMixin):
    """
    A pool handles all streams for a specific token.
    """

    def __init__(self, address: AddressType, factory: Factory):
        self.address = address
        self.factory = factory
        self.contract = self.create_contract(self.address, CONTRACT_TYPES["LlamaPay"])  # type: ignore
        self.token = self.create_contract(self.contract.token(), ERC20)

    @cached_property
    def symbol(self):
        return self.token.symbol()

    @cached_property
    def scale(self):
        return 10 ** self.token.decimals()

    def get_logs(self):
        logs = self.provider.get_contract_logs(
            self.address,
            self.contract.contract_type.events,
            start_block=self.factory.deployment.deploy_block,
            stop_block=self.chain_manager.blocks.height,
            block_page_size=10_000,
        )
        return list(logs)

    def get_balance(self, payer: AddressType) -> Decimal:
        return Decimal(self.contract.getPayerBalance(payer)) / self.scale

    def get_withdrawable_amount(
        self,
        payer: AddressType,
        receiver: AddressType,
        rate_per_sec: int,
    ) -> Decimal:
        result = self.contract.withdrawable(payer, receiver, rate_per_sec)
        return Decimal(result.withdrawableAmount) / self.scale

    def create_stream(
        self,
        receiver: AddressType,
        rate: str,
        **tx_args,
    ) -> ReceiptAPI:
        return self.contract.createStream(receiver, Rate.parse(rate).per_sec, **tx_args)

    def cancel_stream(
        self,
        receiver: AddressType,
        rate_per_sec: int,
        **tx_args,
    ) -> ReceiptAPI:
        return self.contract.cancelStream(receiver, rate_per_sec, **tx_args)

    def pause_stream(
        self,
        receiver: AddressType,
        rate_per_sec: int,
        **tx_args,
    ) -> ReceiptAPI:
        return self.contract.pauseStream(receiver, rate_per_sec, **tx_args)

    def withdraw(
        self,
        payer: AddressType,
        receiver: AddressType,
        rate_per_sec: int,
        **tx_args,
    ) -> ReceiptAPI:
        return self.contract.withdraw(payer, receiver, rate_per_sec, **tx_args)
    def approve(self, amount: Optional[Decimal] = None, **tx_args) -> ReceiptAPI:
        """
        Approve token to be deposited into a pool.

        Arguments:
            amount: decimal amount in tokens [default: infinite]
        """
        amount = 2**256 - 1 if amount is None else amount * self.scale
        return self.token.approve(self.address, amount, **tx_args)

    def deposit(self, amount: Decimal, **tx_args) -> ReceiptAPI:
        """
        Deposit funding balance into a pool.

        Arguments:
            amount: decimal amount in tokens
        """
        if self.token.allowance(tx_args["sender"], self.address) < amount:
            self.approve(amount, **tx_args)

        return self.contract.deposit(amount * self.scale, **tx_args)

    def withdraw(self, amount: Optional[Decimal] = None, **tx_args) -> ReceiptAPI:
        """
        Withdraw funding balance from a pool.

        Arguments:
            amount: decimal amount in tokens [default: withdraw all]
        """
        if amount:
            return self.contract.withdrawPayer(amount * self.scale, **tx_args)
        else:
            return self.contract.withdrawPayerAll(**tx_args)

    def __repr__(self):
        return f"<Pool address={self.address} token={self.symbol}>"

    def __eq__(self, other) -> bool:
        return self.address == other.address


class Stream(BaseModel):
    """
    Represents a payment stream.
    """

    token: Optional[str]
    payer: str
    receiver: str
    rate_per_sec: int
    reason: Optional[str]

    @property
    def stream_id(self) -> bytes:
        return keccak(
            encode_abi_packed(
                ["address", "address", "uint216"],
                [self.payer, self.receiver, self.rate_per_sec],
            )
        )


class Rate(BaseModel):
    amount: Decimal
    period: Literal["day", "week", "month", "year"]
    token: Optional[str]

    @property
    def per_sec(self):
        # this is the amount you feed to llamapay contracts
        return int(self.amount * PRECISION / DURATION_TO_SECONDS[self.period])

    @classmethod
    def parse(cls, rate: str):
        amount, period = rate.split("/")
        assert period in DURATION_TO_SECONDS

        try:
            amount, token = amount.split(maxsplit=2)
        except ValueError:
            amount, token = amount, None

        amount = amount.replace(",", "_")

        return cls(amount=Decimal(amount), period=period, token=token)
