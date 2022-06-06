from functools import cached_property
from pathlib import Path
from typing import List

from ape.contracts import ContractInstance
from ape.types import AddressType
from ape.utils import ManagerAccessMixin
from ape_tokens import tokens
from ape_tokens.managers import ERC20
from ethpm_types import PackageManifest
from ape.exceptions import ConversionError

from ape_llamapay.constants import FACTORY_DEPLOYMENTS

manifest = PackageManifest.parse_file(Path(__file__).parent / "manifest.json")


class PoolNotDeployed(Exception):
    pass


class Factory(ManagerAccessMixin):
    """
    LlamaPay streams for each token are contained in pools.
    This factory helps discover and deploy new pools.
    """

    def __init__(self) -> None:
        self.deployment = FACTORY_DEPLOYMENTS.get(
            ecosystem=self.provider.network.ecosystem.name,
            network=self.provider.network.name.replace("-fork", ""),
        )
        self.contract = self.create_contract(
            self.deployment.address,
            manifest.contract_types["LlamaPayFactory"],  # type: ignore
        )

    def get_pool(self, token: str) -> "Pool":
        """
        Get pool by token address or symbol.
        """
        token = self._resolve_token(token)
        address, is_deployed = self.contract.getLlamaPayContractByToken(token)
        if not is_deployed:
            raise PoolNotDeployed("deterministic address: %s" % address)

        return Pool(address)

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
        pools = [Pool(self.contract.getLlamaPayContractByIndex(i)) for i in range(pool_count)]
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

    def __init__(self, address: AddressType):
        self.address = address

    @cached_property
    def contract(self):
        return ContractInstance(self.address, manifest.contract_types["LlamaPay"])

    @cached_property
    def token(self):
        tok = self.contract.token()
        return ContractInstance(tok, ERC20)

    def __repr__(self):
        return f"<Pool address={self.address} token={self.token.symbol()}>"

    def __eq__(self, other) -> bool:
        return self.address == other.address
