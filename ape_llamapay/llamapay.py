from functools import cached_property
from pathlib import Path

from ape.contracts import ContractInstance
from ape.types import AddressType
from ape.utils import ManagerAccessMixin
from ape_tokens import tokens
from ape_tokens.managers import ERC20
from ethpm_types import PackageManifest

from ape_llamapay.constants import FACTORY

manifest = PackageManifest.parse_file(Path(__file__).parent / "manifest.json")


class Factory(ManagerAccessMixin):
    @property
    def address(self) -> AddressType:
        ecosystem_name = self.provider.network.ecosystem.name
        network_name = self.provider.network.name
        return AddressType(FACTORY[ecosystem_name][network_name])

    @property
    def contract(self) -> ContractInstance:
        return ContractInstance(self.address, manifest.contract_types["LlamaPayFactory"])

    def get_contract_for_token(self, token: str) -> "LlamaPay":
        try:
            token = tokens[token].address
        except KeyError:
            pass

        address, is_deployed = self.contract.getLlamaPayContractByToken(token)
        return LlamaPay(address, is_deployed)


class LlamaPay(ManagerAccessMixin):
    def __init__(self, address: AddressType, is_deployed: bool):
        self.address = address
        self.is_deployed = is_deployed

    @property
    def contract(self):
        return ContractInstance(self.address, manifest.contract_types["LlamaPay"])

    @cached_property
    def token(self):
        return ContractInstance(self.contract.token(), ERC20)

    def __repr__(self):
        return f"<LlamaPay address={self.address} exists={self.is_deployed} token={self.token.symbol()}>"
