"""
Sanity tests for Assignment 1b - Minimal Viable Blockchain.

=== HOW TO USE THIS FILE ===

This file is both your TEST SUITE and your IMPLEMENTATION GUIDE.
Work through the phases in order. After implementing each phase,
run the corresponding tests to verify:

    python3 -m pytest test_sanity.py -v                     # run all
    python3 -m pytest test_sanity.py -k "Phase1" -v         # run only Phase 1
    python3 -m pytest test_sanity.py -k "Phase5" -v         # run only Phase 5

=== IMPLEMENTATION ORDER ===

    Phase 1 → script.py      : sha256_hash(), verify_p2pkh()
    Phase 2 → merkle.py      : double_sha256(), merkle_parent(), build_merkle_tree()
    Phase 3 → block.py       : Block.mine()
    Phase 4 → wallet.py      : build_transaction()
    Phase 5 → node.py        : new_chain(), update_utxos(), is_transaction_valid(),
                                build_block(), append()
    Phase 6 → (end-to-end)   : Everything working together

=== ABOUT UTXO SELECTION ===

In real Bitcoin, a wallet queries the UTXO set and picks which coins to spend
(coin selection). We do NOT implement this. Instead, the test code manually
constructs Input objects that reference specific UTXOs:

    Input(
        previous_tx.outputs[0],   # the Output being spent
        previous_tx_id            # hash of the tx that created it
    )

Your Node code validates that these UTXOs actually exist and that the
signatures are correct. Think of it this way:

    Tests/caller: "I want to spend this specific UTXO"  (picks the Input)
    Wallet:       "OK, I'll sign it"                    (build_transaction)
    Node:         "Let me verify it's real and valid"    (is_transaction_valid)

Passing these does NOT guarantee full marks — the autograder has more tests.
"""

import os
import unittest
from hashlib import sha256
from nacl.signing import SigningKey


# ---------------------------------------------------------------------------
# Reference helpers (self-contained — these do NOT call your code except where
# noted, so they work even before you implement anything)
# ---------------------------------------------------------------------------

ZERO_HASH = '0' * 64
DIFFICULTY = 0x07FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
BLOCK_REWARD = 50


def _keypair():
    """Generate a random (signing_key, public_key_hex) pair."""
    key = SigningKey.generate()
    pub = key.verify_key.encode().hex()
    return key, pub


def _ref_double_sha256(data: bytes) -> bytes:
    return sha256(sha256(data).digest()).digest()


def _ref_merkle_parent(left: str, right: str) -> str:
    combined = bytes.fromhex(left) + bytes.fromhex(right)
    return _ref_double_sha256(combined).hex()


def _tx_bytes(tx):
    """Serialize a transaction to bytes (with scriptSig)."""
    m = b''
    for i in tx.inputs:
        m += i.to_bytes()
    for o in tx.outputs:
        m += o.to_bytes()
    return m


def _tx_bytes_to_sign(tx):
    """Serialize a transaction to bytes for signing (without scriptSig)."""
    m = b''
    for i in tx.inputs:
        m += i.to_bytes_unsigned()
    for o in tx.outputs:
        m += o.to_bytes()
    return m


def _tx_hash(tx):
    """Compute the transaction hash."""
    return sha256(_tx_bytes(tx)).hexdigest()


def _build_and_sign(inputs, outputs, key):
    """
    Reference transaction builder — signs a transaction with the given key.

    This does the same thing your build_transaction() will do, but is
    provided here so Node tests can work before you implement the wallet.

    NOTE: Uses YOUR sha256_hash() (via Output.p2pkh) and YOUR Script class.
    """
    from transaction import Transaction, Input
    from script import Script
    unsigned_inputs = [Input(inp.output, inp.tx_hash, Script([])) for inp in inputs]
    unsigned_tx = Transaction(unsigned_inputs, outputs)
    tx_data = _tx_bytes_to_sign(unsigned_tx)
    signature = key.sign(tx_data).signature.hex()
    pub_key = key.verify_key.encode().hex()
    signed_inputs = []
    for inp in inputs:
        script_sig = Script.p2pkh_unlocking_script(signature, pub_key)
        signed_inputs.append(Input(inp.output, inp.tx_hash, script_sig))
    return Transaction(signed_inputs, outputs)


def _mine_block(prev_hash, transactions):
    """
    Reference block miner — finds a valid nonce for a block.

    This does the same thing your Block.mine() will do, but is provided
    here so Node tests can work before you implement mining.

    NOTE: Uses YOUR build_merkle_tree().
    """
    from block import Block
    from merkle import build_merkle_tree
    if not isinstance(transactions, list):
        transactions = [transactions]
    prev_bytes = bytes.fromhex(prev_hash)
    mr = build_merkle_tree([tx.tx_hash for tx in transactions])
    nonce = 0
    while True:
        m = sha256()
        m.update(prev_bytes)
        m.update(bytes.fromhex(mr))
        m.update(nonce.to_bytes(8, 'big', signed=False))
        if int(m.hexdigest(), 16) < DIFFICULTY:
            break
        nonce += 1
    return Block(prev_hash, transactions, nonce.to_bytes(8, 'big', signed=False).hex())


# ===========================================================================
# Phase 1: Cryptographic primitives  (script.py)
#
# Implement: sha256_hash(), verify_p2pkh()
# These are pure crypto functions with no blockchain dependencies.
#
# Run: python3 -m pytest test_sanity.py -k "Phase1" -v
# ===========================================================================

class TestPhase1_sha256_hash(unittest.TestCase):
    """sha256_hash(data) should return the SHA-256 digest as raw bytes."""

    def test_returns_32_bytes(self):
        from script import sha256_hash
        result = sha256_hash(b'hello')
        self.assertIsInstance(result, bytes)
        self.assertEqual(len(result), 32)

    def test_matches_stdlib(self):
        from script import sha256_hash
        data = b'blockchain'
        self.assertEqual(sha256_hash(data), sha256(data).digest())


class TestPhase1_verify_p2pkh(unittest.TestCase):
    """
    verify_p2pkh(signature, pubkey, expected_pubkey_hash, tx_data) -> bool

    Two checks:
      1. SHA256(pubkey) == expected_pubkey_hash
      2. signature is valid for tx_data under pubkey
    """

    def test_valid_signature(self):
        from script import sha256_hash, verify_p2pkh
        sk, pk = _keypair()
        pubkey = bytes.fromhex(pk)
        pubkey_hash = sha256_hash(pubkey)
        tx_data = b'test transaction data'
        signature = sk.sign(tx_data).signature
        self.assertTrue(verify_p2pkh(signature, pubkey, pubkey_hash, tx_data))

    def test_wrong_signature(self):
        from script import sha256_hash, verify_p2pkh
        sk1, pk1 = _keypair()
        sk2, _ = _keypair()
        pubkey = bytes.fromhex(pk1)
        pubkey_hash = sha256_hash(pubkey)
        tx_data = b'test data'
        wrong_sig = sk2.sign(tx_data).signature
        self.assertFalse(verify_p2pkh(wrong_sig, pubkey, pubkey_hash, tx_data))


# ===========================================================================
# Phase 2: Merkle tree  (merkle.py)
#
# Implement: double_sha256(), merkle_parent(), build_merkle_tree()
# These are independent of Phase 1 — you can work on them in parallel.
#
# Run: python3 -m pytest test_sanity.py -k "Phase2" -v
# ===========================================================================

class TestPhase2_double_sha256(unittest.TestCase):
    """double_sha256(data) = SHA256(SHA256(data)), returns raw bytes."""

    def test_returns_32_bytes(self):
        from merkle import double_sha256
        result = double_sha256(b'test')
        self.assertIsInstance(result, bytes)
        self.assertEqual(len(result), 32)

    def test_matches_reference(self):
        from merkle import double_sha256
        data = b'merkle node'
        self.assertEqual(double_sha256(data), _ref_double_sha256(data))


class TestPhase2_merkle_parent(unittest.TestCase):
    """merkle_parent(left, right) = double_sha256(left_bytes + right_bytes) as hex."""

    def test_basic(self):
        from merkle import merkle_parent
        left = sha256(b'a').hexdigest()
        right = sha256(b'b').hexdigest()
        self.assertEqual(merkle_parent(left, right), _ref_merkle_parent(left, right))

    def test_order_matters(self):
        from merkle import merkle_parent
        left = sha256(b'x').hexdigest()
        right = sha256(b'y').hexdigest()
        self.assertNotEqual(merkle_parent(left, right), merkle_parent(right, left))


class TestPhase2_build_merkle_tree(unittest.TestCase):
    """build_merkle_tree(tx_hashes) returns the Merkle root as a hex string."""

    def test_single_element(self):
        from merkle import build_merkle_tree
        tx = sha256(b'only').hexdigest()
        self.assertEqual(build_merkle_tree([tx]), tx)

    def test_two_elements(self):
        from merkle import build_merkle_tree
        txs = [sha256(b'a').hexdigest(), sha256(b'b').hexdigest()]
        expected = _ref_merkle_parent(txs[0], txs[1])
        self.assertEqual(build_merkle_tree(txs), expected)


# ===========================================================================
# Phase 3: Block mining  (block.py)
#
# Implement: Block.mine()
# Requires: Phase 1 (sha256_hash, for Output.p2pkh) + Phase 2 (merkle tree)
#
# Run: python3 -m pytest test_sanity.py -k "Phase3" -v
# ===========================================================================

class TestPhase3_block_mine(unittest.TestCase):
    """Block.mine() should find a nonce that makes the block hash <= DIFFICULTY."""

    def test_mine_finds_valid_nonce(self):
        from transaction import Transaction, Output
        from block import Block
        k1, p1 = _keypair()
        coinbase = Transaction([], [Output.p2pkh(BLOCK_REWARD, p1)])
        block = Block(prev=ZERO_HASH, txs=[coinbase], nonce=None)
        block.mine()
        self.assertIsNotNone(block.nonce)
        block_hash_int = int(block.hash(), 16)
        self.assertLessEqual(block_hash_int, DIFFICULTY)


# ===========================================================================
# Phase 4: Wallet  (wallet.py)
#
# Implement: build_transaction()
# Requires: Phase 1 (sha256_hash)
#
# Run: python3 -m pytest test_sanity.py -k "Phase4" -v
#
# NOTE: build_transaction() receives PRE-SELECTED inputs. The caller decides
# which UTXOs to spend — your function just validates and signs them.
# ===========================================================================

class TestPhase4_build_transaction(unittest.TestCase):
    """
    build_transaction(inputs, outputs, signing_key) -> Transaction or None

    The caller provides:
      - inputs:  which UTXOs to spend (already chosen for you)
      - outputs: where to send the coins
      - signing_key: the private key to sign with

    Your job: validate, sign, attach scriptSigs, return the Transaction.
    """

    def test_basic_transaction(self):
        from transaction import Transaction, Output, Input
        from wallet import build_transaction

        k1, p1 = _keypair()  # sender
        k2, p2 = _keypair()  # receiver

        # Simulate an existing UTXO: 10000 coins locked to k1.
        # In a real scenario, this Output came from a previous transaction.
        # We use a random hex string as the "previous tx hash" — the wallet
        # doesn't check if UTXOs actually exist, the Node does that later.
        existing_output = Output.p2pkh(10000, p1)
        fake_prev_txid = os.urandom(32).hex()

        tx = build_transaction(
            [Input(existing_output, fake_prev_txid)],   # spend this UTXO
            [Output.p2pkh(10000, p2)],                  # send all to p2
            k1                                          # sign with k1
        )

        self.assertIsInstance(tx, Transaction)
        self.assertEqual(len(tx.inputs), 1)
        self.assertEqual(len(tx.outputs), 1)
        self.assertEqual(tx.outputs[0].value, 10000)


# ===========================================================================
# Phase 5: Node  (node.py)
#
# Implement: new_chain(), update_utxos(), is_transaction_valid(),
#            build_block(), append()
# Requires: Phase 1 + Phase 2 (reference helpers handle mining & signing)
#
# Run: python3 -m pytest test_sanity.py -k "Phase5" -v
#
# === HOW THESE TESTS WORK ===
#
# The tests use _build_and_sign() and _mine_block() — reference helpers
# defined above — so your Node code is tested independently of your wallet
# and mining implementations.
#
# The pattern in every test is:
#
#   1. Create a genesis block with a coinbase → initial UTXO
#   2. Manually construct Input objects referencing known UTXOs
#      (this is the "UTXO selection" — we do it for you, no mempool needed)
#   3. Sign the transaction with _build_and_sign()
#   4. Call node.build_block() or node.append() — YOUR code validates
#
# Your Node checks: does the referenced UTXO exist? Is the signature valid?
# Does input total == output total? Is there no double-spending?
# ===========================================================================

class TestPhase5_build_block(unittest.TestCase):
    """Node.build_block(txs) validates transactions and mines a new block."""

    def test_basic_build_block(self):
        from transaction import Transaction, Output, Input
        from block import Block
        from node import Node

        k1, p1 = _keypair()  # miner / initial coin holder
        k2, p2 = _keypair()  # recipient

        # --- Genesis: create the first coins ---
        # A coinbase transaction has no inputs — new coins appear from thin air.
        genesis_coinbase = Transaction([], [Output.p2pkh(10000, p1)])
        genesis_coinbase_txid = _tx_hash(genesis_coinbase)

        # Mine and register the genesis block.
        genesis_block = _mine_block(ZERO_HASH, genesis_coinbase)
        node = Node()
        node.new_chain(genesis_block)
        # UTXO set now: [{txid: genesis_coinbase_txid, value: 10000, owner: p1}]

        # --- Spend the genesis UTXO ---
        # We MANUALLY select which UTXO to spend by constructing the Input.
        # This is what a wallet + mempool would do in real Bitcoin.
        # Here, we know exactly which UTXO exists because we just created it.
        tx = _build_and_sign(
            [Input(genesis_coinbase.outputs[0], genesis_coinbase_txid)],
            [Output.p2pkh(10000, p2)],
            k1
        )

        # YOUR build_block() should:
        #   1. Find the longest chain
        #   2. Validate the transaction (UTXO exists, signature valid, totals match)
        #   3. Mine and return a new block
        block = node.build_block(tx)
        self.assertIsInstance(block, Block)


class TestPhase5_append(unittest.TestCase):
    """Node.append(block) validates and adds a block to the chain."""

    def test_append_valid_block(self):
        from transaction import Transaction, Output, Input
        from node import Node

        k1, p1 = _keypair()
        k2, p2 = _keypair()

        # Genesis
        genesis_coinbase = Transaction([], [Output.p2pkh(10000, p1)])
        genesis_coinbase_txid = _tx_hash(genesis_coinbase)
        genesis_block = _mine_block(ZERO_HASH, genesis_coinbase)

        node = Node()
        node.new_chain(genesis_block)

        # Build a block (uses YOUR build_block to validate + mine)
        tx = _build_and_sign(
            [Input(genesis_coinbase.outputs[0], genesis_coinbase_txid)],
            [Output.p2pkh(10000, p2)],
            k1
        )
        block = node.build_block(tx)

        # Append should succeed — valid PoW, valid transaction
        result = node.append(block)
        self.assertTrue(result)


# ===========================================================================
# Phase 6: End-to-end walkthrough
#
# Requires: ALL phases implemented.
#
# Run: python3 -m pytest test_sanity.py -k "Phase6" -v
#
# Read through these tests to understand the full UTXO lifecycle:
# how coins are created, spent, split (change), and recombined.
# ===========================================================================

class TestPhase6_lifecycle(unittest.TestCase):
    """
    Follow the money from genesis through multiple transactions.

    This is the full picture of how our blockchain works. The tests use
    _build_and_sign() (the reference helper) so the focus is on the Node
    logic, not the wallet.
    """

    def test_spend_with_change(self):
        """
        Alice gets 50 coins, sends 30 to Bob (keeps 20 as change),
        then Bob sends 30 to Carol.

        This demonstrates:
        - Coinbase: creating money from nothing
        - Change: you must spend entire UTXOs, send remainder back to yourself
        - Chaining: Bob spends the UTXO that Alice's transaction created
        """
        from transaction import Transaction, Output, Input
        from node import Node

        alice_key, alice_pub = _keypair()
        bob_key, bob_pub = _keypair()
        carol_key, carol_pub = _keypair()

        # ----- Genesis: Alice mines the first block, gets 50 coins -----
        coinbase_tx = Transaction([], [Output.p2pkh(50, alice_pub)])
        coinbase_txid = _tx_hash(coinbase_tx)
        genesis = _mine_block(ZERO_HASH, coinbase_tx)

        node = Node()
        node.new_chain(genesis)

        # UTXO set:
        #   Alice: 50 coins (from coinbase)

        # ----- Alice sends 30 to Bob, 20 back to herself -----
        #
        # KEY CONCEPT: You CANNOT partially spend a UTXO.
        # Alice's only UTXO is worth 50. To send 30 to Bob, she must:
        #   - Spend the entire 50-coin UTXO (as an Input)
        #   - Create two Outputs: 30 to Bob + 20 to herself (change)
        #   - Input total (50) must equal Output total (30 + 20 = 50)
        tx1 = _build_and_sign(
            [Input(coinbase_tx.outputs[0], coinbase_txid)],
            [Output.p2pkh(30, bob_pub), Output.p2pkh(20, alice_pub)],
            alice_key
        )
        tx1_id = _tx_hash(tx1)

        block1 = node.build_block(tx1)
        self.assertIsNotNone(block1)
        node.append(block1)

        # UTXO set after block1:
        #   REMOVED: Alice's 50-coin UTXO (spent)
        #   ADDED:   Bob   — 30 coins (tx1, output 0)
        #   ADDED:   Alice — 20 coins (tx1, output 1) ← change!

        # ----- Bob sends his 30 to Carol -----
        # Bob references tx1.outputs[0] — the 30-coin UTXO created above.
        tx2 = _build_and_sign(
            [Input(tx1.outputs[0], tx1_id)],
            [Output.p2pkh(30, carol_pub)],
            bob_key
        )

        block2 = node.build_block(tx2)
        self.assertIsNotNone(block2)
        node.append(block2)

        # Final UTXO set:
        #   Alice: 20 coins (change from tx1)
        #   Carol: 30 coins (from tx2)
        #   Bob:   0 coins  (spent everything)

    def test_combine_multiple_utxos(self):
        """
        Alice splits 50 into two UTXOs (30 + 20), then combines
        them back into a single transaction to send 50 to Bob.

        This demonstrates:
        - Multiple outputs creating separate UTXOs
        - Multiple inputs in one transaction (combining UTXOs)
        """
        from transaction import Transaction, Output, Input
        from node import Node

        alice_key, alice_pub = _keypair()
        bob_key, bob_pub = _keypair()

        # Genesis
        coinbase_tx = Transaction([], [Output.p2pkh(50, alice_pub)])
        coinbase_txid = _tx_hash(coinbase_tx)
        genesis = _mine_block(ZERO_HASH, coinbase_tx)

        node = Node()
        node.new_chain(genesis)

        # Alice splits 50 into two UTXOs: 30 + 20 (both to herself)
        tx1 = _build_and_sign(
            [Input(coinbase_tx.outputs[0], coinbase_txid)],
            [Output.p2pkh(30, alice_pub), Output.p2pkh(20, alice_pub)],
            alice_key
        )
        tx1_id = _tx_hash(tx1)

        block1 = node.build_block(tx1)
        node.append(block1)

        # UTXO set: Alice has TWO separate UTXOs (30 + 20)

        # Alice combines both UTXOs into one transaction to pay Bob 50
        tx2 = _build_and_sign(
            [
                Input(tx1.outputs[0], tx1_id),  # 30 coins
                Input(tx1.outputs[1], tx1_id),  # 20 coins
            ],
            [Output.p2pkh(50, bob_pub)],        # 30 + 20 = 50
            alice_key
        )

        block2 = node.build_block(tx2)
        self.assertIsNotNone(block2)
        node.append(block2)

        # UTXO set: Bob has 50, Alice has nothing


if __name__ == '__main__':
    unittest.main()
