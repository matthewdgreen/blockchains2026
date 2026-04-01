# Assignment 2: Ethereum — Create Your Token (Phase 1)

**Course:** Blockchains and Cryptocurrencies (601.641/441) — Spring 2026

## Learning Objectives

By completing this assignment, you will learn to:

1. **Key management** — Create an Ethereum wallet and securely store your private key
2. **ERC20 token standard** — Understand and implement the ERC20 interface used by tokens across Ethereum
3. **Smart contract development** — Write, compile, and test a Solidity smart contract
4. **Contract deployment** — Deploy a contract to a live testnet and understand gas, transactions, and block confirmations
5. **Contract interaction** — Read state from and send transactions to deployed contracts programmatically
6. **Ethereum tooling** — Use industry-standard tools: Hardhat (development framework), Ethers.js (contract interaction library), Etherscan (block explorer), and OpenZeppelin (audited contract libraries)
7. **On-chain privacy** — Use hash commitments to store identity data without revealing it publicly
8. **Testnet workflow** — Obtain testnet ETH, configure RPC endpoints, and work with the Sepolia network

## Overview

In this assignment you will set up an Ethereum development environment, write and deploy your own ERC20 token to the Sepolia testnet, and register it with the course's on-chain Registry contract.

This is Phase 1 of a multi-part assignment. In later phases you will use your token to interact with a decentralized exchange and a DAO.

## Prerequisites

- Node.js v20+
  - **macOS/Linux:** `nvm install 20` (install nvm from [nvm-sh/nvm](https://github.com/nvm-sh/nvm) if needed)
  - **Windows:** Install [nvm-windows](https://github.com/coreybutler/nvm-windows/releases) (download `nvm-setup.exe`), then open a new terminal and run `nvm install 20` followed by `nvm use 20`
- A browser wallet (e.g., MetaMask)
- Sepolia testnet ETH (see faucets below)

### Getting Sepolia Testnet ETH

You need a small amount of Sepolia ETH to pay for gas when deploying and interacting with contracts. Use one of these faucets:

- [Google Cloud Faucet](https://cloud.google.com/application/web3/faucet/ethereum/sepolia) — No account required, 0.05 ETH/day
- [Alchemy Faucet](https://www.alchemy.com/faucets/ethereum-sepolia) — Requires free Alchemy account
- [Infura Faucet](https://www.infura.io/faucet/sepolia) — Requires free Infura account
- [PoW Faucet](https://sepolia-faucet.pk910.de/) — Mine testnet ETH in your browser, no account required

If you have trouble getting testnet ETH, contact the TA.

## Setup

```
cd starter
npm install
cp .env.example .env
```

Edit `.env` with:
- An RPC URL from [Infura](https://www.infura.io/) or [Alchemy](https://www.alchemy.com/) (free tier)
- Your wallet's private key
- The Registry contract address (provided by the TA)

## Part 1: Create Your ERC20 Token

Edit `contracts/StudentToken.sol`. Your token must:

- Inherit from OpenZeppelin's ERC20
- Have a non-empty name and symbol
- Have a `totalSupply` of at least 1,000,000 tokens (with 18 decimals)
- Assign tokens to the deployer on construction

Read the [OpenZeppelin ERC20 documentation](https://docs.openzeppelin.com/contracts/5.x/erc20) and the `IRegistry` interface in `contracts/interfaces/IRegistry.sol` to understand the requirements.

Run the local test suite to check your work:

```
npx hardhat test
```

All tests should pass before you deploy.

## Part 2: Deploy to Sepolia

Write your deployment logic in `scripts/deploy-token.js`. See the [Hardhat deployment guide](https://hardhat.org/hardhat-runner/docs/guides/deploying).

```
npx hardhat run scripts/deploy-token.js --network sepolia
```

Save your deployed contract address.

## Part 3: Register with the Course Registry

The TA has deployed a Registry contract on Sepolia. Its interface is in `contracts/interfaces/IRegistry.sol` — read it carefully.

Write your registration logic in `scripts/register.js`. You will need to:

1. Connect to the Registry contract on Sepolia
2. Compute a **name hash**: `keccak256(abi.encodePacked(name, secret))` where `name` is a Solidity `string` and `secret` is a `uint256`. In ethers.js:
   ```js
   ethers.solidityPackedKeccak256(["string", "uint256"], ["Firstname Lastname", 42n])
   ```
   This is a privacy-preserving identity commitment: your real name is **not** stored on-chain, only the hash is. Remember your secret.
3. Call `registerStudent(tokenAddress, nameHash)` on the Registry

```
npx hardhat run scripts/register.js --network sepolia
```

After registering, **submit your secret (the uint256 number) to the TA via Gradescope** so your identity can be verified.

## What to Submit (Gradescope)

Upload a single file:

- `StudentToken.sol` — your token contract source code

The autograder will compile your contract, deploy it to a local test network, and verify it meets the Registry requirements.

Additionally, submit the following via the Gradescope questionnaire:

1. Your deployed token address on Sepolia
2. Your wallet address
3. Your full name (exactly as used in the name hash, e.g., `Firstname Lastname`)
4. Your secret — a uint256 number (e.g., `42`)

The TA will verify your on-chain commitment by computing `keccak256(abi.encodePacked(name, secret))` and checking it matches the `nameHash` stored in the Registry. Use **exactly the same name and secret** as when you registered — any difference (capitalization, spacing, etc.) will produce a different hash.

The TA will verify your on-chain registration separately.

## Grading (Phase 1 — 20 points)

This is Phase 1 of a multi-part assignment. Later phases will add up to a total of 100 points.

| Component | Points | Verified by |
|---|---|---|
| Deploys with valid name, symbol, and decimals | 2 | Autograder |
| Total supply >= 1,000,000 and deployer holds tokens | 2 | Autograder |
| transfer() and approve()/transferFrom() work | 4 | Autograder |
| Passes full Registry integration check | 2 | Autograder |
| Token deployed to Sepolia | 5 | Course staff |
| Registered with the Registry on Sepolia | 5 | Course staff |

## Resources

- [Solidity Documentation](https://docs.soliditylang.org/)
- [OpenZeppelin ERC20](https://docs.openzeppelin.com/contracts/5.x/erc20)
- [Hardhat Documentation](https://hardhat.org/docs)
- [Ethers.js v6 Documentation](https://docs.ethers.org/v6/)
- [Sepolia Etherscan](https://sepolia.etherscan.io/)
