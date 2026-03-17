// deploy-pair.js
// Deploys your SimplePair contract for your StudentToken and the GOV token.
//
// Required environment variables:
//   STUDENT_TOKEN_ADDRESS  - Address of your deployed StudentToken
//   GOV_TOKEN_ADDRESS      - Address of the TA's GovernanceToken (GOV)

const hre = require("hardhat");

async function main() {
  const { STUDENT_TOKEN_ADDRESS, GOV_TOKEN_ADDRESS } = process.env;

  if (!STUDENT_TOKEN_ADDRESS || !GOV_TOKEN_ADDRESS) {
    console.error("Missing required environment variables.");
    console.error("Set STUDENT_TOKEN_ADDRESS and GOV_TOKEN_ADDRESS in your .env file.");
    process.exit(1);
  }

  const [deployer] = await hre.ethers.getSigners();
  console.log("Deploying SimplePair with account:", deployer.address);

  const balance = await hre.ethers.provider.getBalance(deployer.address);
  console.log("Account balance:", hre.ethers.formatEther(balance), "ETH");

  console.log("\nDeploying SimplePair...");
  console.log("  TokenA (StudentToken):", STUDENT_TOKEN_ADDRESS);
  console.log("  TokenB (GOV):", GOV_TOKEN_ADDRESS);

  const SimplePair = await hre.ethers.getContractFactory("SimplePair");
  const pair = await SimplePair.deploy(STUDENT_TOKEN_ADDRESS, GOV_TOKEN_ADDRESS);
  await pair.waitForDeployment();

  const pairAddress = await pair.getAddress();
  console.log("\nSimplePair deployed at:", pairAddress);
  console.log("\nAdd this to your .env:");
  console.log(`PAIR_ADDRESS=${pairAddress}`);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
