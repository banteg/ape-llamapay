import pkgutil
from datetime import timedelta
from typing import List

from ethpm_types import PackageManifest
from pydantic import BaseModel

manifest = pkgutil.get_data(__package__, "manifest.json")
CONTRACT_TYPES = PackageManifest.parse_raw(manifest).contract_types  # type: ignore


class FactoryDeployment(BaseModel):
    ecosystem: str
    network: str
    address: str
    deploy_block: int

    class Config:
        allow_mutation = False


class Deplyoments(BaseModel):
    __root__: List[FactoryDeployment]

    def get(self, ecosystem, network):
        return next(
            item
            for item in self.__root__
            if item.ecosystem == ecosystem and item.network == network
        )


FACTORY_DEPLOYMENTS = Deplyoments(
    __root__=[
        FactoryDeployment(
            ecosystem="ethereum",
            network="mainnet",
            address="0xde1C04855c2828431ba637675B6929A684f84C7F",
            deploy_block=14_676_643,
        ),
        FactoryDeployment(
            ecosystem="ethereum",
            network="rinkeby",
            address="0xde1C04855c2828431ba637675B6929A684f84C7F",
            deploy_block=10_582_060,
        ),
        FactoryDeployment(
            ecosystem="ethereum",
            network="kovan",
            address="0xD43bB75Cc924e8475dFF2604b962f39089e4f842",
            deploy_block=31_267_493,
        ),
        FactoryDeployment(
            ecosystem="optimism",
            network="mainnet",
            address="0xde1C04855c2828431ba637675B6929A684f84C7F",
            # transaction index, TODO verify if it works as intended
            deploy_block=6_699_902,
        ),
        FactoryDeployment(
            ecosystem="arbitrum",
            network="mainnet",
            address="0xde1C04855c2828431ba637675B6929A684f84C7F",
            deploy_block=10_785_890,
        ),
        FactoryDeployment(
            ecosystem="avalanche",
            network="mainnet",
            address="0x7d507b4c2d7e54da5731f643506996da8525f4a3",
            deploy_block=13_948_155,
        ),
        FactoryDeployment(
            ecosystem="avalanche",
            network="fuji",
            address="0xc4705f96030D347F421Fbe01d9A19F18B26a7d30",
            deploy_block=9_057_940,
        ),
        FactoryDeployment(
            ecosystem="fantom",
            network="opera",
            address="0xde1C04855c2828431ba637675B6929A684f84C7F",
            deploy_block=37_130_440,
        ),
        FactoryDeployment(
            ecosystem="polygon",
            network="mainnet",
            address="0xde1C04855c2828431ba637675B6929A684f84C7F",
            deploy_block=27_671_043,
        ),
        FactoryDeployment(
            ecosystem="bsc",
            network="mainnet",
            address="0xde1C04855c2828431ba637675B6929A684f84C7F",
            deploy_block=17_356_891,
        ),
        FactoryDeployment(
            # provisional name, there is no gnosis chain / xdai plugin yet
            ecosystem="gnosis",
            network="mainnet",
            address="0xde1C04855c2828431ba637675B6929A684f84C7F",
            deploy_block=21_881_219,
        ),
    ]
)


DURATION_TO_SECONDS = {
    period: int(timedelta(days=days).total_seconds())
    for period, days in [
        ("day", 1),
        ("week", 7),
        ("month", 30),
        ("year", 360),  # come at me sambacha
    ]
}

PRECISION = 10**20
