# Assignment 2 - Phase 3: DAO Governance Exploit

**Course:** Blockchains and Cryptocurrencies (601.641/441) - Spring 2026

**Due Date:** Saturday, April 26, 2026, 11:59 PM ET

## Overview

Welcome to the course DAO. As of Phase 2, every registered student holds GOV tokens, which means you are all now members of our on-chain governance system. The GovernanceDAO contract controls grade assignment for this course: only the designated TA can call `setGrade()`.

Here's the problem: the TA and CAs are swamped this semester and don't have time to grade your assignment. So we're going to let you do it yourselves. The GovernanceDAO has a `setGrade(student, grade)` function that records your grade on-chain (max 100). If you can figure out how to call it, the TA will simply read your grade from the blockchain. Saves everyone time.

There's just one catch: only the current TA address can call `setGrade()`, and that's not you. The DAO has a governance mechanism that *could* change the TA, but you'd need over 1,000,000 GOV votes to pass a proposal, and you only have 1,000 GOV. Good luck with that.

Unless, of course, you find another way.

**Your objective:** Set your own grade on-chain. You can choose any grade from 0 to 100.

**What you will learn:**
- Flash loan mechanics and how they enable atomic arbitrage
- How delegation-based governance works (and how it can go wrong)
- Why real-world DAOs like Compound and Uniswap use historical balance snapshots
- Writing multi-step exploit contracts that execute atomically
- The Beanstalk-style governance attack vector

## Background

### Governance DAOs

Decentralized Autonomous Organizations (DAOs) allow token holders to govern a protocol through on-chain voting. A typical governance flow works like this:

1. A token holder **delegates** their voting power (often to themselves)
2. Anyone with enough voting power can **propose** an action
3. Token holders **vote** on the proposal
4. If the proposal reaches **quorum** (enough votes), it can be **executed**

The executed proposal calls a function on a target contract, for example, changing a protocol parameter or granting a role.

### Flash Loans

A flash loan lets you borrow tokens with **no collateral**, as long as you repay them within the same transaction. If repayment fails, the entire transaction reverts as if nothing happened.

```
┌─────────── Single Transaction ───────────┐
│                                          │
│  1. Borrow 2,000,000 tokens              │
│  2. Do something with them...            │
│  3. Repay 2,000,000 tokens               │
│                                          │
│  If step 3 fails → everything reverts    │
└──────────────────────────────────────────┘
```

Flash loans are a legitimate DeFi primitive used for arbitrage, liquidations, and collateral swaps. But they have also been used to exploit governance protocols with weak voting mechanisms.

### Real-World Precedent: Beanstalk (April 2022)

In April 2022, an attacker exploited Beanstalk Farms' governance system using a flash loan. The attacker borrowed a massive amount of tokens, used them to gain governance power, passed a malicious proposal, and drained $182 million from the protocol, all in a single transaction. The root cause: the governance system measured voting power based on current token holdings rather than historical snapshots.

## Deployed Contracts (Sepolia)

The TA has deployed three contracts on Sepolia:

| Contract | Address |
|----------|---------|
| GovernanceToken (GOV) | `0x4e6081534784F6A2EdC5455713F163B05a03466d` |
| LendingPool | `0x781d5a896FB5E5C31359F47EB6774816fbdd2ff9` |
| GovernanceDAO | `0x4Bc1EeBFec45EF87EDbd700A475a53Eae5E9E5E1` |

### GovernanceToken (GOV)

The same ERC20 token from Phase 2. It serves as the governance token for the DAO and as the asset available for flash loans in the LendingPool.

### LendingPool

Holds 2,000,000 GOV tokens and offers flash loans. When you call `flashLoan(amount)`:

1. The pool transfers `amount` GOV tokens to your contract
2. The pool calls `onFlashLoan(amount)` on your contract (you must implement `IFlashLoanReceiver`)
3. After your callback returns, the pool verifies its balance is at least what it was before

If the balance check fails, the entire transaction reverts.

### GovernanceDAO

A delegation-based governance contract. Key functions:

- **`delegate(delegatee)`** - Records your current GOV balance as voting power for the delegatee. Each address can only delegate once.
- **`propose(description, target, data)`** - Creates a proposal to call `target` with `data`. Requires voting power.
- **`vote(proposalId)`** - Votes in favor of a proposal using your voting power.
- **`execute(proposalId)`** - Executes a proposal if it has reached quorum (1,000,000 GOV votes).
- **`setTA(newTA)`** - Changes the TA address. Can only be called by the DAO itself (i.e., via a governance proposal).
- **`setGrade(student, grade)`** - Sets a student's grade (0-100). Can only be called by the current TA.

Read `contracts/interfaces/IGovernanceDAO.sol` and `contracts/interfaces/ILendingPool.sol` for the complete interface specifications.

## Your Task

### Implement `Attacker.sol`

Create `contracts/Attacker.sol` that implements the `IAttacker` interface (see `contracts/interfaces/IAttacker.sol`). Your contract must implement:

```solidity
// Entry point for your exploit. Must complete in a single transaction.
function attack() external;

// Callback invoked by LendingPool during a flash loan.
// You must repay the full loan amount before this function returns.
function onFlashLoan(uint256 amount) external;
```

Your contract must also:

1. **Set your grade (0-100)** in the GovernanceDAO
2. **Complete everything in a single transaction** (the `attack()` call)
3. **Not drain the LendingPool** - all borrowed tokens must be repaid

Your constructor must accept three addresses in this order:
```solidity
constructor(address _lendingPool, address _dao, address _governanceToken)
```

The test suite and deploy script expect this constructor signature. Beyond that, the internal design of your contract is up to you. Study the interfaces and the GovernanceDAO source code to find the vulnerability and figure out how to exploit it.

### Recommended Workflow

We recommend completing this assignment in the following order:

1. **Answer Q1 and Q2 first** (Aave and Terra/LUNA in `submission.tex`). These questions build your understanding of lending protocols, flash loans, and how protocol design flaws lead to catastrophic failures.
2. **Answer Q3** (Flash Loans). This directly prepares you for the coding portion. You'll need to understand the callback mechanism to implement your exploit.
3. **Implement `Attacker.sol`** and test locally with `npx hardhat test`.
4. **Deploy to Sepolia** and verify with `check-status.js`.
5. **Answer Q4** (Your Attack Sequence). Explain what you built and why it works.

### Success Criteria

After your `attack()` transaction succeeds:
- `dao.grades(yourAddress)` returns your chosen grade (0-100)
- `dao.ta()` returns your address
- The LendingPool's GOV balance is unchanged

## Setup

```bash
cd Assignments/assignment_2/phase3/starter
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
LENDING_POOL_ADDRESS=0x781d5a896FB5E5C31359F47EB6774816fbdd2ff9
DAO_ADDRESS=0x4Bc1EeBFec45EF87EDbd700A475a53Eae5E9E5E1
```

## File Structure

```
contracts/
  interfaces/
    IAttacker.sol         - Interface your contract must implement
    IGovernanceDAO.sol    - GovernanceDAO interface (READ THIS)
    ILendingPool.sol      - LendingPool + IFlashLoanReceiver interfaces (READ THIS)
  GovernanceDAO.sol       - DAO contract with a vulnerability (READ THIS)
  GovernanceToken.sol     - GOV token (for local testing)
  LendingPool.sol         - Flash loan pool (for local testing)
  Attacker.sol            - YOUR IMPLEMENTATION (create this file)
scripts/
  deploy-attacker.js      - Deploy your Attacker and run the exploit on Sepolia
  check-status.js         - Check your grade on-chain
test/
  Attacker.test.js        - Local tests for your exploit
```

## Testing Locally

Run the provided tests to verify your exploit works:

```bash
npx hardhat test
```

All 4 tests should pass before deploying to Sepolia.

## Deploying to Sepolia

Once your local tests pass, deploy and execute the exploit on Sepolia:

```bash
npx hardhat run scripts/deploy-attacker.js --network sepolia
```

This deploys your Attacker contract and calls `attack()`. If successful, you will see your new grade printed in the output.

To check your status at any time:

```bash
npx hardhat run scripts/check-status.js --network sepolia
```

**Note:** If your exploit reverts on-chain, the transaction fails atomically and no state changes persist. You can fix your contract and redeploy as many times as needed.

## Submission

Submit the following to **Gradescope** under **Assignment 2 - Phase 3**:

1. **Autograder submission:** Upload your `Attacker.sol` file only. The autograder will compile and test your contract automatically.
2. **Written submission:** Fill in `submission.tex`, compile to PDF, and upload separately.

### What is graded

| Test | Points | Description |
|------|--------|-------------|
| Compilation | 2 | Contract compiles without errors |
| Grade set | 4 | `dao.grades(student)` is between 1-100 after `attack()` |
| TA changed | 4 | `dao.ta()` is the student's address after `attack()` |
| Single transaction | 2 | Exploit completes in one `attack()` call |
| Pool not drained | 2 | LendingPool balance unchanged after exploit |
| **Total** | **14** | |

## Resources

### Flash Loans and DeFi Lending
- [Aave Documentation](https://docs.aave.com/)
- [Aave Flash Loans](https://docs.aave.com/developers/guides/flash-loans)
- [Aave V3 Overview](https://docs.aave.com/faq/aave-v3-features)
- [Finematics: Flash Loans Explained](https://www.youtube.com/watch?v=mCJUhnXQ76s)
- [Finematics: Aave Explained](https://www.youtube.com/watch?v=WwE3lUq51gQ)

### Terra/LUNA Collapse
- [Coindesk: The Fall of Terra](https://www.coindesk.com/learn/the-fall-of-terra-a-timeline-of-the-meteoric-rise-and-crash-of-ust-and-luna/)
- [Nansen: Demystifying TerraUSD Depegging](https://www.nansen.ai/research/on-chain-forensics-demystifying-terrausd-de-peg)
- [Finematics: Algorithmic Stablecoins Explained](https://www.youtube.com/watch?v=S7-rfvpEpJs)
- [MakerDAO Documentation (DAI)](https://docs.makerdao.com/)

### Governance Exploits
- [Beanstalk Governance Exploit (Rekt News)](https://rekt.news/beanstalk-rekt/)
- [OpenZeppelin Governor (secure governance)](https://docs.openzeppelin.com/contracts/5.x/governance)
- [ERC20Votes: snapshot-based voting](https://docs.openzeppelin.com/contracts/5.x/api/token/erc20#ERC20Votes)

### Solidity Reference
- [Solidity by Example: ABI Encoding](https://solidity-by-example.org/abi-encode/)
- [OpenZeppelin ERC20](https://docs.openzeppelin.com/contracts/5.x/erc20)
