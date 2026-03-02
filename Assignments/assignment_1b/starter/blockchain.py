from typing import List

from block import Block

"""
Blockchain data structure - a chain of blocks with UTXO tracking.
"""


class Blockchain:
    """
    A blockchain. This class is provided for convenience only; the autograder
    will not call this class.
    """

    def __init__(self, chain: List[Block], utxos: List[str]):
        self.chain = chain
        self.utxos = utxos

    def append(self, block: Block) -> bool:
        # TODO
        pass
