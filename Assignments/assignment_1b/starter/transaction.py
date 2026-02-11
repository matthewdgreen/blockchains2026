import hashlib
from typing import List

from script import Script, sha256_hash, OP_DUP, OP_SHA256, OP_EQUALVERIFY, OP_CHECKSIG

DIFFICULTY = 0x07FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
BLOCK_REWARD = 50  # Coinbase reward for mining a block (in satoshis)

"""
Core transaction data structures for the blockchain with Bitcoin Script support.

This implements a simplified UTXO (Unspent Transaction Output) model similar to Bitcoin.
Each transaction consumes existing UTXOs as inputs and creates new UTXOs as outputs.
"""


class Output:
    """
    A transaction output with a locking script (scriptPubKey).

    The script_pubkey defines the conditions that must be met to spend this output.
    For P2PKH, this is: OP_DUP OP_SHA256 <pubKeyHash> OP_EQUALVERIFY OP_CHECKSIG
    """

    def __init__(self, value: int, script_pubkey: Script):
        self.value = value
        self.script_pubkey = script_pubkey

    @staticmethod
    def p2pkh(value: int, pub_key: str) -> 'Output':
        """
        Create a P2PKH (Pay to Public Key Hash) output.

        This is the most common output type. Funds are locked to a public key hash,
        and can only be spent by providing a valid signature from the corresponding
        private key.
        """
        pub_key_hash = sha256_hash(bytes.fromhex(pub_key)).hex()
        return Output(value, Script.p2pkh_locking_script(pub_key_hash))

    def to_bytes(self) -> bytes:
        """Serialize the output to bytes."""
        # TODO: Serialize value (4 bytes, big-endian) + script_pubkey bytes
        pass


class Input:
    """
    A transaction input with an unlocking script (scriptSig).

    The tx_hash refers to the hash of the transaction where this input was created.
    The script_sig provides the data needed to satisfy the locking script.
    """

    def __init__(self, output: Output, tx_hash: str, script_sig: Script = None):
        self.output = output
        self.tx_hash = tx_hash
        self.script_sig = script_sig if script_sig is not None else Script([])

    def to_bytes(self) -> bytes:
        """Serialize the input to bytes (including script_sig)."""
        return self.output.to_bytes() + bytes.fromhex(self.tx_hash) + self.script_sig.to_bytes()

    def to_bytes_unsigned(self) -> bytes:
        """Serialize without the script_sig (for signing)."""
        return self.output.to_bytes() + bytes.fromhex(self.tx_hash)


class Transaction:
    """
    A transaction in a block.

    There are two types of transactions:
    1. Regular transactions: Spend existing UTXOs, must have valid signatures
    2. Coinbase transactions: Create new coins as block reward, no inputs required

    Unlike the simple version, signatures are now in each input's script_sig
    rather than a single signature for the whole transaction.
    """

    def __init__(self, inputs: List[Input], outputs: List[Output]):
        self.inputs = inputs
        self.outputs = outputs
        self.tx_hash = self.get_hash()

    def get_hash(self) -> str:
        """Compute the SHA256 hash of the serialized transaction."""
        # TODO: Compute and return the SHA256 hash (hex string) of self.to_bytes()
        pass

    @staticmethod
    def coinbase(miner_pub_key: str, reward: int = BLOCK_REWARD) -> 'Transaction':
        """
        Create a coinbase transaction (block reward).

        Coinbase transactions are special:
        - They have no inputs (new coins are created)
        - They reward the miner for finding a valid block
        - They are always the first transaction in a block

        In real Bitcoin, the coinbase also includes block height and extra nonce.
        """
        output = Output.p2pkh(reward, miner_pub_key)
        return Transaction([], [output])

    def is_coinbase(self) -> bool:
        """Check if this is a coinbase transaction (no inputs)."""
        return len(self.inputs) == 0

    def bytes_to_sign(self) -> str:
        """
        Get the bytes of the transaction for signing.

        This excludes the script_sig from inputs, as signatures can't sign themselves.
        """
        m = b''
        for i in self.inputs:
            m += i.to_bytes_unsigned()
        for o in self.outputs:
            m += o.to_bytes()
        return m.hex()

    def to_bytes(self) -> str:
        """Serialize the complete transaction including scripts."""
        m = b''
        for i in self.inputs:
            m += i.to_bytes()
        for o in self.outputs:
            m += o.to_bytes()
        return m.hex()
