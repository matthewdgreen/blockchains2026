// scripts/check-status.js
//
// Check the current state of the GovernanceDAO for your account.
//
// Usage:
//   npx hardhat run scripts/check-status.js --network sepolia

const hre = require("hardhat");

async function main() {
  const daoAddress = process.env.DAO_ADDRESS;
  const govTokenAddress = process.env.GOV_TOKEN_ADDRESS;
  const lendingPoolAddress = process.env.LENDING_POOL_ADDRESS;

  if (!daoAddress || !govTokenAddress || !lendingPoolAddress) {
    console.error("Error: DAO_ADDRESS, GOV_TOKEN_ADDRESS, and LENDING_POOL_ADDRESS must be set in .env");
    process.exit(1);
  }

  const [account] = await hre.ethers.getSigners();
  const dao = await hre.ethers.getContractAt("IGovernanceDAO", daoAddress);
  const govToken = await hre.ethers.getContractAt("IERC20", govTokenAddress);

  const grade = await dao.grades(account.address);
  const currentTA = await dao.ta();
  const isTA = currentTA === account.address;

  console.log("=== GovernanceDAO Status ===");
  console.log("Account:       ", account.address);
  console.log("Current TA:    ", currentTA);
  console.log("You are TA:    ", isTA ? "YES" : "NO");
  console.log("Your grade:    ", grade.toString());
  console.log("GOV balance:   ", hre.ethers.formatEther(await govToken.balanceOf(account.address)));
  console.log("Pool balance:  ", hre.ethers.formatEther(await govToken.balanceOf(lendingPoolAddress)), "GOV");
  console.log("Proposals:     ", (await dao.proposalCount()).toString());
  console.log("");

  if (grade === 100n && isTA) {
    console.log("Result: PASS - Exploit successful! Grade is 100 and you are the TA.");
  } else if (grade === 100n) {
    console.log("Result: PARTIAL - Grade is 100 but you are not the TA.");
  } else {
    console.log("Result: INCOMPLETE - Exploit not yet successful.");
  }
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
