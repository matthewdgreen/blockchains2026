from typing import Optional, List, Union

from script import Script, verify_p2pkh
from transaction import Transaction, Output, Input, DIFFICULTY, BLOCK_REWARD
from block import Block
from blockchain import Blockchain

"""
Network node that manages multiple blockchain forks.

=== NAKAMOTO CONSENSUS ===

This implementation follows Nakamoto Consensus, the breakthrough innovation
that allows a decentralized network to agree on a single transaction history
without a central authority.

Key principles:

1. LONGEST CHAIN RULE
   - Always consider the longest valid chain as the "true" chain
   - When you receive a new block, add it to whatever chain it extends
   - When building a new block, always build on the longest chain
   - This ensures all honest nodes eventually converge on the same chain

2. TIE-BREAKING
   - When two chains have equal length, stick with the one you saw first
   - Only switch to a different chain if it becomes longer
   - This prevents unnecessary chain reorganizations

3. PROOF OF WORK
   - Miners must find a nonce that makes the block hash below DIFFICULTY
   - This makes it computationally expensive to create blocks
   - An attacker would need >50% of network hashpower to rewrite history

4. BLOCK REWARDS (Coinbase)
   - Miners receive newly created coins for finding valid blocks
   - This incentivizes honest mining behavior
   - Coinbase transactions have no inputs - they create new money

5. FORK HANDLING
   - Temporary forks are normal when two miners find blocks simultaneously
   - The network naturally resolves forks as one chain becomes longer
   - Transactions in orphaned blocks return to the mempool
"""


class Node:
    """
    All chains that the node is currently aware of.
    """

    def __init__(self):
        # We will not access this field, you are free change it if needed.
        self.chains = []

    def new_chain(self, genesis: Block):
        """
        Create a new chain with the given genesis block.
        The autograder will give you the genesis block.

        The genesis block is special:
        - It's the first block in the chain (no previous block)
        - Its coinbase transaction creates the initial coins
        - All nodes must agree on the same genesis block

        You need to:
        1. Create UTXOs from all transactions in the genesis block
        2. Create a new Blockchain with the genesis block
        3. Add the blockchain to self.chains

        Note: Genesis block has block.txs (a list of transactions)
        """
        # TODO: Implement new_chain
        # Hint: Loop through genesis.txs and for each tx, create UTXOs from outputs
        pass

    def append(self, block: Block) -> bool:
        """
        Attempt to append a block broadcast on the network.
        Returns True if it is possible to add (e.g. could be a fork), False otherwise.

        === NAKAMOTO CONSENSUS: FORK HANDLING ===

        When a new block arrives, we don't immediately know if it will be
        part of the longest chain. Two miners might find valid blocks at
        nearly the same time, creating a temporary fork.

        Our strategy:
        1. Accept ALL valid blocks that extend ANY known chain tip
        2. Each valid block creates a new "fork" in our view
        3. When building blocks, we always choose the longest fork
        4. Eventually, one fork will become longer and "win"

        You need to:
        1. Find a chain where the block's prev hash matches the last block
        2. Validate the block (PoW and all transactions)
        3. Create a new chain (fork) with the block appended
        4. Update UTXOs for all transactions in the block
        """
        # TODO: Implement append
        # Hint: block.txs is a list of transactions - update UTXOs for each
        pass

    def build_block(self, txs: List[Transaction]) -> Optional[Block]:
        """
        Build a block on the longest chain you are currently tracking.
        Returns None if any transaction is invalid (e.g. double spend).

        Accepts a list of transactions to include in the block.
        For convenience, also accepts a single Transaction (auto-wrapped in list).

        === NAKAMOTO CONSENSUS: LONGEST CHAIN RULE ===

        This method implements a core principle of Nakamoto Consensus:
        always build on the longest valid chain.

        Why? Because the longest chain represents the most cumulative
        proof-of-work, meaning the most computational effort was spent
        on it. An attacker trying to rewrite history would need to
        outpace the entire honest network.

        You need to:
        1. Find the longest chain (use max() with key=len)
        2. Validate all transactions against that chain's UTXOs
           - First transaction can be coinbase
           - Transactions can spend outputs from earlier txs in same block
        3. Create and mine a new block with Block(prev, txs, nonce)
        """
        # TODO: Implement build_block
        # Hint: If txs is a single Transaction, wrap it in a list first
        # Hint: Use a temporary UTXO set to validate transactions in order
        pass

    def is_valid_block(self, block: Block, chain: Blockchain) -> bool:
        """Validate a block's proof of work and all transactions."""
        if not self.verify_pow(block):
            return False

        if not block.txs:
            return False

        # Validate all transactions with a temporary UTXO set
        # This allows transactions in the same block to spend outputs
        # created by earlier transactions in the same block
        temp_utxos = [utxo.copy() for utxo in chain.utxos]
        temp_chain = Blockchain(chain=chain.chain.copy(), utxos=temp_utxos)

        for i, tx in enumerate(block.txs):
            # First transaction can be coinbase
            is_coinbase_allowed = (i == 0)
            if not self.is_transaction_valid(tx, temp_chain, is_coinbase_allowed):
                return False
            # Update temp UTXOs so next transaction can spend outputs from this one
            self.update_utxos(temp_chain, tx)

        return True

    def is_transaction_valid(self, tx: Transaction, blockchain: Blockchain, is_coinbase_allowed: bool = False) -> bool:
        """
        Validate a transaction.

        For coinbase transactions:
        - Must have no inputs (check tx.is_coinbase())
        - Output value must not exceed BLOCK_REWARD
        - Only allowed as the first transaction in a block

        For regular transactions:
        1. Find the UTXO being spent for each input
        2. Extract signature and pubkey from scriptSig (input.script_sig.elements)
        3. Extract expected pubkey hash from scriptPubKey (input.output.script_pubkey.elements[2])
        4. Use verify_p2pkh() to validate the signature
        5. Input total must equal output total (no inflation)

        Also check:
        - No double-spending within the transaction
        """
        # TODO: Implement transaction validation
        # Hint: Check tx.is_coinbase() first and handle separately
        # Hint: For regular transactions, extract from scripts:
        #       - signature = bytes.fromhex(input.script_sig.elements[0])
        #       - pubkey = bytes.fromhex(input.script_sig.elements[1])
        #       - expected_hash = bytes.fromhex(input.output.script_pubkey.elements[2])
        #       - tx_data = bytes.fromhex(tx.bytes_to_sign())
        # Hint: Use verify_p2pkh(signature, pubkey, expected_hash, tx_data)
        pass

    def update_utxos(self, blockchain: Blockchain, tx: Transaction):
        """
        Update UTXO set after a transaction is confirmed.

        1. Remove UTXOs that were spent by the transaction's inputs
        2. Add new UTXOs from the transaction's outputs
        """
        # TODO: Implement UTXO updates
        pass

    def verify_pow(self, block: Block) -> bool:
        """Verify proof of work meets difficulty requirement."""
        block_hash = int(block.hash(), 16)
        return block_hash <= DIFFICULTY

    def find_transaction(self, blockchain: Blockchain, tx_number: str) -> Optional[Transaction]:
        """Find a transaction by its number in the blockchain."""
        for block in blockchain.chain:
            for tx in block.txs:
                if tx.number == tx_number:
                    return tx
        return None
