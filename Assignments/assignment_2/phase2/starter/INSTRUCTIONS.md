# Assignment 2 --- Phase 2: Simplified Uniswap V2 AMM

**Course:** Blockchains and Cryptocurrencies (601.641/441) --- Spring 2026

**Due Date:** Sunday, April 5, 2026, 11:59 PM ET

## Overview

In this phase you will implement a **simplified Uniswap V2 pair contract** --- a constant-product automated market maker (AMM). Your contract enables trustless token swaps between your StudentToken (from Phase 1) and the TA's Governance Token (GOV) using the `x * y = k` invariant.

**What you will learn:**
- How constant-product AMMs work (the math behind Uniswap V2)
- Liquidity provision and LP token mechanics
- Swap fee calculation (0.3%)
- Deploying and interacting with contracts on a live testnet

## Architecture

### How Uniswap V2 Works

In real Uniswap V2, a **Factory** contract deploys **Pair** contracts for each token pair. Each Pair is an independent AMM that holds reserves of two tokens and allows swaps using the constant product formula `x * y = k`.

```
┌─────────────────────────────────────────────────────────────────┐
│                    UNISWAP V2 ARCHITECTURE                      │
│                                                                 │
│  ┌──────────┐    deploys     ┌──────────────┐                   │
│  │ Factory  │ ─────────────> │  Pair (A/B)  │                   │
│  │          │    deploys     ├──────────────┤                   │
│  │          │ ─────────────> │  Pair (A/C)  │                   │
│  └──────────┘    deploys     ├──────────────┤                   │
│                ─────────────>│  Pair (B/C)  │                   │
│                              └──────────────┘                   │
│                                                                 │
│  Each Pair holds reserves of two ERC20 tokens and               │
│  enables swaps using x * y = k with a 0.3% fee.                 │
└─────────────────────────────────────────────────────────────────┘
```

### What We're Building (Simplified)

In this assignment, you skip the Factory and **deploy a Pair contract directly**. Your SimplePair connects your StudentToken from Phase 1 with the TA's Governance Token (GOV).

```
┌─────────────────────── SEPOLIA TESTNET ───────────────────────┐
│                                                               │
│   TA deploys:                                                 │
│   ┌─────────────────┐         ┌──────────────┐                │
│   │ GovernanceToken │ ──────> │   Registry   │                │
│   │     (GOV)       │  airdrop│  (Phase 1)   │                │
│   │  10M supply     │  1,000  └──────┬───────┘                │
│   └────────┬────────┘  GOV to        │                        │
│            │           each          │ has student            │
│            │           student       │ addresses              │
│            │                         │                        │
│   Student deploys:                   │                        │
│   ┌────────────────┐                 │                        │
│   │  StudentToken  │◄────────────────┘                        │
│   │   (Phase 1)    │                                          │
│   └────────┬───────┘                                          │
│            │                                                  │
│            │  tokenA    ┌──────────────────────┐   tokenB     │
│            └───────────>│     SimplePair       │<─────────┐   │
│                         │    (YOUR CODE)       │          │   │
│                         │                      │          │   │
│                         │  ┌────────────────┐  │   ┌──────┴─┐ │
│                         │  │ Reserve:       │  │   │  GOV   │ │
│                         │  │  StudentToken  │  │   │ Token  │ │
│                         │  │  GOV Token     │  │   └────────┘ │
│                         │  │                │  │              │
│                         │  │ LP Tokens:     │  │              │
│                         │  │  track shares  │  │              │
│                         │  └────────────────┘  │              │
│                         │                      │              │
│                         │  addLiquidity()      │              │
│                         │  removeLiquidity()   │              │
│                         │  swap()              │              │
│                         └──────────────────────┘              │
│                                                               │
└───────────────────────────────────────────────────────────────┘
```

### The Swap Flow

When a user swaps tokens through your SimplePair:

```
 User                        SimplePair                    Tokens
  │                              │                           │
  │  1. approve(pair, amount)    │                           │
  │─────────────────────────────────────────────────────────>│
  │                              │                           │
  │  2. swap(tokenIn, amountIn)  │                           │
  │─────────────────────────────>│                           │
  │                              │  3. transferFrom(user)    │
  │                              │──────────────────────────>│
  │                              │                           │
  │                              │  4. Calculate amountOut   │
  │                              │     using x * y = k       │
  │                              │     with 0.3% fee         │
  │                              │                           │
  │                              │  5. transfer(user, out)   │
  │                              │──────────────────────────>│
  │                              │                           │
  │  6. Receive tokenOut         │                           │
  │<─────────────────────────────────────────────────────────│
```

### The Constant Product Formula

For a detailed explanation of how the `x * y = k` invariant works, including the math behind swaps, fees, and liquidity provision, see the [Uniswap V2 documentation](https://docs.uniswap.org/contracts/v2/concepts/protocol-overview/how-uniswap-works).

## Prerequisites

- Completed Phase 1 (deployed StudentToken, registered in Registry)
- Your StudentToken contract address
- Sepolia testnet ETH in your wallet
- Node.js 20+ (`nvm use 20`)

## Contract Addresses (Sepolia)

| Contract | Address |
|----------|---------|
| Registry | `0x335f43d6CCFfF66F115D99819158A21c6c6efb10` |
| GovernanceToken (GOV) | `0x4e6081534784F6A2EdC5455713F163B05a03466d` |

The TA will airdrop **1,000 GOV tokens** to each registered student's wallet.

## Your Task

### Implement `SimplePair.sol`

Create `contracts/SimplePair.sol` that implements the `ISimplePair` interface (see `contracts/interfaces/ISimplePair.sol`).

Your contract must:

1. **Accept two token addresses in its constructor:**
   ```solidity
   constructor(address _tokenA, address _tokenB)
   ```

2. **Track LP tokens internally** using a `mapping(address => uint256)` and a `uint256 totalSupply` (does not need to be a full ERC20).

3. **Implement the following functions:**

#### `addLiquidity(uint256 amountA, uint256 amountB) -> uint256 liquidity`

Deposits `amountA` of tokenA and `amountB` of tokenB into the pool. Caller must `approve()` both tokens to the pair contract first.

- **First provider:** `liquidity = sqrt(amountA * amountB)`
- **Subsequent providers:** `liquidity = min(amountA * totalLP / reserveA, amountB * totalLP / reserveB)`
- Both amounts must be > 0
- Emit `LiquidityAdded(provider, amountA, amountB, liquidity)`

#### `removeLiquidity(uint256 liquidity) -> (uint256 amountA, uint256 amountB)`

Burns LP tokens and returns proportional share of the reserves.

- `amountA = liquidity * reserveA / totalLP`
- `amountB = liquidity * reserveB / totalLP`
- Caller must have sufficient LP balance
- Emit `LiquidityRemoved(provider, amountA, amountB, liquidity)`

#### `swap(address tokenIn, uint256 amountIn) -> uint256 amountOut`

Swaps `amountIn` of `tokenIn` for the other token using the constant product formula with a **0.3% fee**:

```
amountOut = (reserveOut * amountIn * 997) / (reserveIn * 1000 + amountIn * 997)
```

- `tokenIn` must be either tokenA or tokenB
- Caller must `approve()` tokenIn to the pair contract first
- Emit `Swap(user, tokenIn, amountIn, amountOut)`

#### `getReserves() -> (uint256 reserveA, uint256 reserveB)`

Returns the current reserves of both tokens.

#### `tokenA()` and `tokenB()`

Return the addresses of the two tokens.

### Hints

- Use OpenZeppelin's `SafeERC20` for token transfers (`safeTransferFrom`, `safeTransfer`)
- For the square root function, implement the [Babylonian method](https://en.wikipedia.org/wiki/Methods_of_computing_square_roots#Heron's_method):
  ```solidity
  function _sqrt(uint256 y) internal pure returns (uint256 z) {
      if (y > 3) {
          z = y;
          uint256 x = y / 2 + 1;
          while (x < z) {
              z = x;
              x = (y / x + x) / 2;
          }
      } else if (y != 0) {
          z = 1;
      }
  }
  ```
- Read the `ISimplePair.sol` interface carefully --- the NatSpec comments contain the exact formulas you need

## Setup

```bash
cd Assignments/assignment_2/phase2/starter
nvm use 20
npm install
```

Copy `.env.example` to `.env` and fill in:
```bash
cp .env.example .env
```

Required `.env` values:
```
SEPOLIA_RPC_URL=https://sepolia.infura.io/v3/YOUR_KEY
PRIVATE_KEY=your_private_key
GOV_TOKEN_ADDRESS=0x4e6081534784F6A2EdC5455713F163B05a03466d
STUDENT_TOKEN_ADDRESS=<your Phase 1 token>
PAIR_ADDRESS=<filled after you deploy the pair>
```

## File Structure

```
contracts/
  interfaces/
    ISimplePair.sol       - Interface your contract must implement
  test/
    MockERC20.sol         - Mock token used by local tests
  SimplePair.sol          - YOUR IMPLEMENTATION (create this file)
scripts/
  deploy-pair.js          - Deploy your SimplePair to Sepolia
  add-liquidity.js        - Approve tokens and add liquidity
  swap.js                 - Perform a swap through your pair
test/
  SimplePair.test.js      - Local tests for your implementation
```

## Testing Locally

Run the provided tests to verify your implementation:

```bash
npx hardhat test
```

All 11 tests should pass before deploying to Sepolia.

## Deploying to Sepolia

### Step 1: Deploy Your Pair

```bash
npx hardhat run scripts/deploy-pair.js --network sepolia
```

This deploys your SimplePair contract with your StudentToken and GOV as the two tokens. Save the pair address in your `.env` as `PAIR_ADDRESS`.

### Step 2: Add Liquidity

```bash
npx hardhat run scripts/add-liquidity.js --network sepolia
```

This approves and deposits your tokens into the pair. The default amounts are 10,000 StudentToken and 500 GOV --- adjust in the script as needed (you only have 1,000 GOV total).

### Step 3: Perform a Swap

```bash
npx hardhat run scripts/swap.js --network sepolia
```

This swaps 100 GOV for your StudentToken through the pair.

## Submission

Upload your `SimplePair.sol` to **Gradescope** under **Assignment 2 - Phase 2**.

Also fill in `submission.tex`, compile to PDF, and upload alongside your contract.

### What is graded

| Test | Points | Description |
|------|--------|-------------|
| Compilation | 1 | Contract compiles without errors |
| Constructor | 1 | `tokenA()` and `tokenB()` return correct addresses |
| addLiquidity (first) | 2 | First LP gets `sqrt(amountA * amountB)` tokens |
| addLiquidity (subsequent) | 2 | Subsequent LP gets proportional tokens |
| swap formula | 2 | Swap output matches constant product formula with 0.3% fee |
| swap reserves | 1 | Reserves update correctly after swap |
| removeLiquidity | 2 | Returns proportional share of reserves |
| Event emission | 1 | All three events emitted correctly |
| **Total** | **12** | |

## Resources

- [Uniswap V2 Whitepaper](https://uniswap.org/whitepaper.pdf)
- [Uniswap V2 Core (UniswapV2Pair.sol)](https://github.com/Uniswap/v2-core/blob/master/contracts/UniswapV2Pair.sol)
- [OpenZeppelin ERC20](https://docs.openzeppelin.com/contracts/5.x/erc20)
- [Constant Product AMM (Solidity by Example)](https://solidity-by-example.org/defi/constant-product-amm/)
