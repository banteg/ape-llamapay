from decimal import Decimal
from functools import cached_property
from typing import List, Optional

from ape.types import AddressType
from ape.utils import ManagerAccessMixin
from ape_tokens import tokens
from ape_tokens.managers import ERC20
from eth_abi.packed import encode_abi_packed
from eth_utils import keccak
from pydantic import BaseModel

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

    def create_pool(self, token: str, **kwargs) -> "Pool":
        """
        Create a pool for a token and return it.
        """
        token = self._resolve_token(token)
        self.contract.createLlamaPayContract(token, **kwargs)

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
        return Decimal(self.contract.balances(payer)) / self.scale

    def __repr__(self):
        return f"<Pool address={self.address} token={self.symbol}>"

    def __eq__(self, other) -> bool:
        return self.address == other.address


class Stream(BaseModel):
    """
    Represents a payment stream.
    """

    sender: str
    receiver: str
    rate: int
    reason: Optional[str]

    @property
    def stream_id(self) -> bytes:
        return keccak(
            encode_abi_packed(
                ["address", "address", "uint216"],
                [self.sender, self.receiver, self.rate],
            )
        )
