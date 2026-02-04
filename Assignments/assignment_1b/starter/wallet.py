from typing import List, Optional
from nacl.signing import SigningKey
from nacl.encoding import HexEncoder

from script import Script, sha256_hash
from transaction import Input, Output, Transaction

"""
Wallet functionality for building and signing transactions.
"""


def build_transaction(inputs: List[Input], outputs: List[Output], signing_key: SigningKey) -> Optional[Transaction]:
    """
    Build and sign a transaction with the given inputs and outputs.

    This creates P2PKH unlocking scripts (scriptSig) for each input.
    Returns None if impossible to build a valid transaction.
    Does not verify that inputs are unspent.

    Validation checks:
    - Inputs and outputs must not be empty
    - All inputs must be spendable by the signing key (pub_key_hash matches)
    - Input values must equal output values
    - No duplicate inputs (same txid)

    Steps:
    1. Validate inputs and outputs
    2. Check that the signing key can spend all inputs
    3. Create an unsigned transaction (empty scriptSigs)
    4. Sign the transaction data
    5. Create scriptSig for each input with signature and public key
    6. Return the signed transaction
    """
    # TODO: Implement build_transaction
    # Hint: Use Script.p2pkh_unlocking_script(signature, pub_key) for scriptSig
    pass
