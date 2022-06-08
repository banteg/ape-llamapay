import pkgutil
from datetime import timedelta
from typing import List

from numpy import block

from ethpm_types import PackageManifest
from pydantic import BaseModel

from hashlib import sha256
import json
import time


class Block:
    def __init__(self, index, transactions, timestamp, previous_hash):
        self.index = index
        self.transactions = transactions
        self.timestamp = timestamp
        self.previous_hash = previous_hash
        self.nonce = 0

    def compute_hash(self):
        """
        A function that return the hash of the block contents.
        """
        block_string = json.dumps(self.__dict__, sort_keys=True)
        return sha256(block_string.encode()).hexdigest()


class Blockchain:
    # difficulty of our PoW algorithm
    difficulty = 2

    def __init__(self):
        self.unconfirmed_transactions = []
        self.chain = []
        self.create_genesis_block()

    def create_genesis_block(self):
        """
        A function to generate genesis block and appends it to
        the chain. The block has index 0, previous_hash as 0, and
        a valid hash.
        """
        genesis_block = Block(0, [], time.time(), "0")
        genesis_block.hash = genesis_block.compute_hash()
        self.chain.append(genesis_block)

    @property
    def last_block(self):
        return self.chain[-1]

    def add_block(self, block, proof):
        """
        A function that adds the block to the chain after verification.
        Verification includes:
        * Checking if the proof is valid.
        * The previous_hash referred in the block and the hash of latest block
          in the chain match.
        """
        previous_hash = self.last_block.hash

        if previous_hash != block.previous_hash:
            return False

        if not self.is_valid_proof(block, proof):
            return False

        block.hash = proof
        self.chain.append(block)
        return True

    def is_valid_proof(self, block, block_hash):
        """
        Check if block_hash is valid hash of block and satisfies
        the difficulty criteria.
        """
        return (block_hash.startswith('0' * Blockchain.difficulty) and
                block_hash == block.compute_hash())

    def proof_of_work(self, block):
        """
        Function that tries different values of nonce to get a hash
        that satisfies our difficulty criteria.
        """
        block.nonce = 0

        computed_hash = block.compute_hash()
        while not computed_hash.startswith('0' * Blockchain.difficulty):
            block.nonce += 1
            computed_hash = block.compute_hash()

        return computed_hash

    def add_new_transaction(self, transaction):
        self.unconfirmed_transactions.append(transaction)

    def mine(self):
        """
        This function serves as an interface to add the pending
        transactions to the blockchain by adding them to the block
        and figuring out Proof Of Work.
        """
        if not self.unconfirmed_transactions:
            return False

        last_block = self.last_block

        new_block = Block(index=last_block.index + 1,
                          transactions=self.unconfirmed_transactions,
                          timestamp=time.time(),
                          previous_hash=last_block.hash)

        proof = self.proof_of_work(new_block)
        self.add_block(new_block, proof)

        self.unconfirmed_transactions = []
        return new_block.index

def decentralizedDaysInYear(): 
    blockchain = Blockchain()
    blockchain.add_new_transaction(5)
    blockchain.mine()
    blockchain.add_new_transaction(6)
    blockchain.mine()
    blockchain.add_new_transaction(3)
    blockchain.mine()

    year = 0
    for i, block in enumerate(blockchain.chain):
        if len(block.transactions) > 0:
            year = year + 10 ** (i-1) * block.transactions[0]

    return year

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
        ("year", decentralizedDaysInYear()),  # come at me sambacha
    ]
}

PRECISION = 10**20
