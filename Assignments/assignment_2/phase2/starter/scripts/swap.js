// swap.js
// Swaps GOV tokens for StudentTokens through your SimplePair.
//
// Required environment variables:
//   PAIR_ADDRESS       - Address of your deployed SimplePair
//   GOV_TOKEN_ADDRESS  - Address of the TA's GovernanceToken (GOV)

const hre = require("hardhat");

async function main() {
  const { PAIR_ADDRESS, GOV_TOKEN_ADDRESS } = process.env;

  if (!PAIR_ADDRESS || !GOV_TOKEN_ADDRESS) {
    console.error("Missing required environment variables.");
    console.error("Set PAIR_ADDRESS and GOV_TOKEN_ADDRESS");
    process.exit(1);
  }

  const [signer] = await hre.ethers.getSigners();
  console.log("Swapping with account:", signer.address);

  const swapAmount = hre.ethers.parseEther("100");

  // Get GOV token contract
  const govToken = await hre.ethers.getContractAt("IERC20", GOV_TOKEN_ADDRESS);

  // Check balance
  const balance = await govToken.balanceOf(signer.address);
  console.log("GOV balance:", hre.ethers.formatEther(balance));

  if (balance < swapAmount) {
    console.error("Insufficient GOV balance. Need", hre.ethers.formatEther(swapAmount));
    process.exit(1);
  }

  // Get pair contract and print reserves before swap
  const pair = await hre.ethers.getContractAt("ISimplePair", PAIR_ADDRESS);

  const [reserveABefore, reserveBBefore] = await pair.getReserves();
  console.log("\nReserves before swap:");
  console.log("  reserveA:", hre.ethers.formatEther(reserveABefore));
  console.log("  reserveB:", hre.ethers.formatEther(reserveBBefore));

  // Approve GOV token to the pair
  console.log("\nApproving GOV token...");
  let tx = await govToken.approve(PAIR_ADDRESS, swapAmount);
  await tx.wait();
  console.log("GOV approved.");

  // Execute swap
  console.log("\nSwapping", hre.ethers.formatEther(swapAmount), "GOV for StudentToken...");
  tx = await pair.swap(GOV_TOKEN_ADDRESS, swapAmount);
  const receipt = await tx.wait();
  console.log("Transaction hash:", receipt.hash);

  // Print reserves after swap
  const [reserveAAfter, reserveBAfter] = await pair.getReserves();
  console.log("\nReserves after swap:");
  console.log("  reserveA:", hre.ethers.formatEther(reserveAAfter));
  console.log("  reserveB:", hre.ethers.formatEther(reserveBAfter));

  console.log("\nSwap completed successfully!");
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
