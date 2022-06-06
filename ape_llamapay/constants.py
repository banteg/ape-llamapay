from typing import List
from pydantic import BaseModel


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
            item for item in self if item.ecosystem == ecosystem and item.network == network
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
