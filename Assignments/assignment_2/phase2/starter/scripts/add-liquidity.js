// add-liquidity.js
// Approves tokens and adds liquidity to your SimplePair.
//
// Required environment variables:
//   PAIR_ADDRESS           - Address of your deployed SimplePair
//   STUDENT_TOKEN_ADDRESS  - Address of your deployed StudentToken
//   GOV_TOKEN_ADDRESS      - Address of the TA's GovernanceToken (GOV)

const hre = require("hardhat");

async function main() {
  const { PAIR_ADDRESS, STUDENT_TOKEN_ADDRESS, GOV_TOKEN_ADDRESS } = process.env;

  if (!PAIR_ADDRESS || !STUDENT_TOKEN_ADDRESS || !GOV_TOKEN_ADDRESS) {
    console.error("Missing required environment variables.");
    console.error("Set PAIR_ADDRESS, STUDENT_TOKEN_ADDRESS, and GOV_TOKEN_ADDRESS");
    process.exit(1);
  }

  const [signer] = await hre.ethers.getSigners();
  console.log("Adding liquidity with account:", signer.address);

  // Amounts to deposit (adjust as needed)
  // You only have 1,000 GOV from the airdrop — don't deposit all of it!
  const amountStudentToken = hre.ethers.parseEther("10000");
  const amountGov = hre.ethers.parseEther("500");

  // Get token contracts
  const studentToken = await hre.ethers.getContractAt("IERC20", STUDENT_TOKEN_ADDRESS);
  const govToken = await hre.ethers.getContractAt("IERC20", GOV_TOKEN_ADDRESS);

  // Check balances
  const balStudent = await studentToken.balanceOf(signer.address);
  const balGov = await govToken.balanceOf(signer.address);
  console.log("StudentToken balance:", hre.ethers.formatEther(balStudent));
  console.log("GOV balance:", hre.ethers.formatEther(balGov));

  if (balStudent < amountStudentToken) {
    console.error("Insufficient StudentToken balance. Need", hre.ethers.formatEther(amountStudentToken));
    process.exit(1);
  }
  if (balGov < amountGov) {
    console.error("Insufficient GOV balance. Need", hre.ethers.formatEther(amountGov));
    process.exit(1);
  }

  // Approve tokens to the pair contract
  console.log("\nApproving StudentToken...");
  let tx = await studentToken.approve(PAIR_ADDRESS, amountStudentToken);
  await tx.wait();
  console.log("StudentToken approved.");

  console.log("Approving GOV token...");
  tx = await govToken.approve(PAIR_ADDRESS, amountGov);
  await tx.wait();
  console.log("GOV approved.");

  // Add liquidity — match token ordering to the pair contract
  const pair = await hre.ethers.getContractAt("ISimplePair", PAIR_ADDRESS);
  const pairTokenA = await pair.tokenA();

  let depositAmountA, depositAmountB;
  if (pairTokenA.toLowerCase() === STUDENT_TOKEN_ADDRESS.toLowerCase()) {
    depositAmountA = amountStudentToken;
    depositAmountB = amountGov;
  } else {
    depositAmountA = amountGov;
    depositAmountB = amountStudentToken;
  }

  console.log("\nAdding liquidity...");
  console.log("  amountA:", hre.ethers.formatEther(depositAmountA));
  console.log("  amountB:", hre.ethers.formatEther(depositAmountB));

  tx = await pair.addLiquidity(depositAmountA, depositAmountB);
  const receipt = await tx.wait();
  console.log("Transaction hash:", receipt.hash);

  // Print reserves
  const [reserveA, reserveB] = await pair.getReserves();
  console.log("\nPool reserves after adding liquidity:");
  console.log("  reserveA:", hre.ethers.formatEther(reserveA));
  console.log("  reserveB:", hre.ethers.formatEther(reserveB));

  console.log("\nLiquidity added successfully!");
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
