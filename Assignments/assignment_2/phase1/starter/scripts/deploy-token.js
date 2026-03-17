// scripts/deploy-token.js
//
// Deploy your StudentToken contract.
//
// Usage:
//   Local:   npx hardhat run scripts/deploy-token.js
//   Sepolia: npx hardhat run scripts/deploy-token.js --network sepolia
//
// See: https://hardhat.org/hardhat-runner/docs/guides/deploying

const hre = require("hardhat");

async function main() {
  const [deployer] = await hre.ethers.getSigners();
  console.log("Deploying with account:", deployer.address);

  // TODO: Deploy your StudentToken and print the contract address.
  //       Save the address — you'll need it for registration.
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
