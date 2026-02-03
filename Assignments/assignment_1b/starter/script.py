import hashlib
from typing import List
from nacl.signing import VerifyKey
from nacl.exceptions import BadSignatureError

"""
Bitcoin Script implementation for P2PKH (Pay to Public Key Hash).

This is a simplified, educational version using human-readable opcodes.
"""

# Opcodes (simplified, human-readable)
OP_DUP = 'OP_DUP'
OP_HASH160 = 'OP_HASH160'
OP_EQUALVERIFY = 'OP_EQUALVERIFY'
OP_CHECKSIG = 'OP_CHECKSIG'

# Set of all opcodes for easy checking
OPCODES = {OP_DUP, OP_HASH160, OP_EQUALVERIFY, OP_CHECKSIG}


def hash160(data: bytes) -> bytes:
    """
    RIPEMD160(SHA256(data)) - Bitcoin's standard hash for public keys.

    This is used to create the public key hash in P2PKH transactions.
    """
    # TODO: Implement hash160
    # 1. Hash the data with SHA256
    # 2. Hash the result with RIPEMD160
    #
    # Hint: Try hashlib.new('ripemd160'), but on some systems (Ubuntu 22.04)
    # RIPEMD160 is disabled. Use try/except and fall back to pycryptodome:
    #   from Crypto.Hash import RIPEMD160
    #   RIPEMD160.new(data).digest()
    pass


class Script:
    """
    A Bitcoin script - a list of opcodes and data pushes.

    Data elements are hex strings, opcodes are string constants (OP_*).
    Elements that are not opcodes are treated as data to push onto the stack.
    """

    def __init__(self, elements: List[str]):
        self.elements = elements

    def to_bytes(self) -> bytes:
        """
        Serialize the script to bytes for hashing.

        Each element is converted to bytes and concatenated:
        - Opcodes are encoded as their string representation (UTF-8)
        - Data elements (hex strings) are converted to bytes
        """
        # TODO: Implement serialization
        pass

    @staticmethod
    def p2pkh_locking_script(pub_key_hash: str) -> 'Script':
        """
        Create a P2PKH locking script (scriptPubKey).

        Format: OP_DUP OP_HASH160 <pubKeyHash> OP_EQUALVERIFY OP_CHECKSIG

        This script locks funds to a public key hash. To spend, the spender
        must provide a signature and public key that hashes to this value.
        """
        return Script([OP_DUP, OP_HASH160, pub_key_hash, OP_EQUALVERIFY, OP_CHECKSIG])

    @staticmethod
    def p2pkh_unlocking_script(signature: str, pub_key: str) -> 'Script':
        """
        Create a P2PKH unlocking script (scriptSig).

        Format: <signature> <pubKey>

        This script provides the signature and public key needed to unlock
        a P2PKH output.
        """
        return Script([signature, pub_key])

    def __repr__(self):
        return f"Script({self.elements})"


class ScriptInterpreter:
    """
    Executes Bitcoin scripts on a stack.

    The interpreter processes each element:
    - Opcodes trigger operations on the stack
    - Data elements are pushed onto the stack

    For P2PKH, the combined script executes as:
    1. Push signature (from scriptSig)
    2. Push pubKey (from scriptSig)
    3. OP_DUP: Duplicate pubKey
    4. OP_HASH160: Hash the duplicated pubKey
    5. Push expected pubKeyHash (from scriptPubKey)
    6. OP_EQUALVERIFY: Verify hashes match
    7. OP_CHECKSIG: Verify signature
    """

    def __init__(self):
        self.stack: List[bytes] = []

    def execute(self, script: Script, tx_data: bytes) -> bool:
        """
        Execute a script. tx_data is used for OP_CHECKSIG.

        Returns True if script succeeds (stack top is truthy), False otherwise.

        Process each element in the script:
        - If it's an opcode, execute the corresponding operation
        - If it's data (hex string), push it onto the stack

        The script succeeds if:
        - No errors occurred during execution
        - The stack is non-empty
        - The top of the stack is truthy (not empty or zero)
        """
        # TODO: Implement script execution
        # Hint: Loop through script.elements, check if each is an opcode or data
        # Use try/except to catch errors and return False
        pass

    def _op_dup(self):
        """
        OP_DUP: Duplicate the top stack element.

        Stack: [..., a] -> [..., a, a]
        """
        # TODO: Implement OP_DUP
        pass

    def _op_hash160(self):
        """
        OP_HASH160: Replace top element with RIPEMD160(SHA256(element)).

        Stack: [..., data] -> [..., hash160(data)]
        """
        # TODO: Implement OP_HASH160
        pass

    def _op_equalverify(self) -> bool:
        """
        OP_EQUALVERIFY: Check top two elements are equal.

        Stack: [..., a, b] -> [...]
        Returns False if a != b, True if a == b.

        Note: This operation removes both elements from the stack.
        """
        # TODO: Implement OP_EQUALVERIFY
        pass

    def _op_checksig(self, tx_data: bytes):
        """
        OP_CHECKSIG: Verify signature against public key and tx_data.

        Stack: [..., signature, pubKey] -> [..., result]

        Uses the public key to verify that the signature is valid for tx_data.
        Pushes b'\\x01' (true) if valid, b'\\x00' (false) if invalid.

        Hint: Use VerifyKey from nacl.signing to verify the signature.
        """
        # TODO: Implement OP_CHECKSIG
        pass
