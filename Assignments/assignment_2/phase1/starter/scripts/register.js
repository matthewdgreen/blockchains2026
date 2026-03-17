// scripts/register.js
//
// Register your wallet and token with the course Registry contract.
//
// Usage:
//   npx hardhat run scripts/register.js --network sepolia
//
// Before running:
//   1. Deploy your StudentToken and note the address
//   2. Read the IRegistry interface to understand what registerStudent() expects

const hre = require("hardhat");

const REGISTRY_ADDRESS = process.env.REGISTRY_ADDRESS || "0x335f43d6CCFfF66F115D99819158A21c6c6efb10";

async function main() {
  const [signer] = await hre.ethers.getSigners();
  console.log("Registering with address:", signer.address);

  // TODO:
  //   1. Connect to the Registry using the IRegistry interface
  //   2. Compute your nameHash: keccak256(abi.encodePacked(yourName, yourSecret))
  //      where yourSecret is a uint256 (e.g., 123456789)
  //      (look up ethers.solidityPackedKeccak256 with types ["string", "uint256"])
  //   3. Call registerStudent(tokenAddress, nameHash)
  //   4. Submit your secret (the uint256 number) to the TA via Gradescope
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
