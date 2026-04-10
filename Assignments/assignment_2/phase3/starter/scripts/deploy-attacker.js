// scripts/deploy-attacker.js
//
// Deploys your Attacker contract and executes the exploit on Sepolia.
//
// Required env vars:
//   LENDING_POOL_ADDRESS - Address of the TA's LendingPool contract
//   DAO_ADDRESS          - Address of the TA's GovernanceDAO contract
//   GOV_TOKEN_ADDRESS    - Address of the GOV token
//
// Usage:
//   npx hardhat run scripts/deploy-attacker.js --network sepolia

const hre = require("hardhat");

async function main() {
  const lendingPoolAddress = process.env.LENDING_POOL_ADDRESS;
  const daoAddress = process.env.DAO_ADDRESS;
  const govTokenAddress = process.env.GOV_TOKEN_ADDRESS;

  if (!lendingPoolAddress || !daoAddress || !govTokenAddress) {
    console.error("Error: LENDING_POOL_ADDRESS, DAO_ADDRESS, and GOV_TOKEN_ADDRESS must be set in .env");
    process.exit(1);
  }

  const [attacker] = await hre.ethers.getSigners();
  console.log("Attacking with account:", attacker.address);

  // Check DAO state before attack
  const dao = await hre.ethers.getContractAt("IGovernanceDAO", daoAddress);
  console.log("\n=== Before Attack ===");
  console.log("Current TA:", await dao.ta());
  console.log("Your grade:", (await dao.grades(attacker.address)).toString());

  // Deploy Attacker contract
  console.log("\nDeploying Attacker contract...");
  const Attacker = await hre.ethers.getContractFactory("Attacker");
  const attackerContract = await Attacker.deploy(
    lendingPoolAddress,
    daoAddress,
    govTokenAddress
  );
  await attackerContract.waitForDeployment();
  console.log("Attacker deployed to:", attackerContract.target);

  // Execute the attack
  console.log("\nExecuting attack...");
  const tx = await attackerContract.attack();
  const receipt = await tx.wait();
  console.log("Attack transaction:", receipt.hash);
  console.log("Gas used:", receipt.gasUsed.toString());

  // Check DAO state after attack
  console.log("\n=== After Attack ===");
  console.log("Current TA:", await dao.ta());
  console.log("Your grade:", (await dao.grades(attacker.address)).toString());

  // Verify success
  const newTA = await dao.ta();
  const grade = await dao.grades(attacker.address);
  if (newTA === attacker.address && grade >= 1n && grade <= 100n) {
    console.log(`\nExploit successful! You are the TA with grade ${grade}.`);
  } else {
    console.log("\nExploit failed. Check your Attacker contract logic.");
  }
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
