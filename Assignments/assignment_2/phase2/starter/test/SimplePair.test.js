// SimplePair.test.js
//
// Tests for your SimplePair contract implementation.
//
// IMPORTANT: You must create contracts/SimplePair.sol that implements the
// ISimplePair interface. Your contract should:
//   - Accept two token addresses in its constructor: constructor(address _tokenA, address _tokenB)
//   - Track LP token balances internally (or inherit ERC20 for LP tokens)
//   - Implement addLiquidity, removeLiquidity, swap, getReserves, tokenA, tokenB
//
// These tests deploy your SimplePair directly (not through the factory) so you
// can validate your implementation locally before deploying to Sepolia.

const { expect } = require("chai");
const hre = require("hardhat");

describe("SimplePair", function () {
  let tokenA, tokenB, pair;
  let owner, alice, bob;

  const INITIAL_MINT = hre.ethers.parseEther("1000000"); // 1M tokens each

  beforeEach(async function () {
    [owner, alice, bob] = await hre.ethers.getSigners();

    // Deploy mock tokens
    const MockERC20 = await hre.ethers.getContractFactory("MockERC20");
    tokenA = await MockERC20.deploy("Token A", "TKA");
    tokenB = await MockERC20.deploy("Token B", "TKB");
    await tokenA.waitForDeployment();
    await tokenB.waitForDeployment();

    // Deploy the student's SimplePair
    const SimplePair = await hre.ethers.getContractFactory("SimplePair");
    pair = await SimplePair.deploy(
      await tokenA.getAddress(),
      await tokenB.getAddress()
    );
    await pair.waitForDeployment();

    // Mint tokens to alice and bob
    await tokenA.mint(alice.address, INITIAL_MINT);
    await tokenB.mint(alice.address, INITIAL_MINT);
    await tokenA.mint(bob.address, INITIAL_MINT);
    await tokenB.mint(bob.address, INITIAL_MINT);
  });

  describe("tokenA / tokenB", function () {
    it("should return the correct token addresses", async function () {
      expect(await pair.tokenA()).to.equal(await tokenA.getAddress());
      expect(await pair.tokenB()).to.equal(await tokenB.getAddress());
    });
  });

  describe("addLiquidity", function () {
    it("first provider receives sqrt(amountA * amountB) LP tokens", async function () {
      const amountA = hre.ethers.parseEther("10000");
      const amountB = hre.ethers.parseEther("10000");

      await tokenA.connect(alice).approve(await pair.getAddress(), amountA);
      await tokenB.connect(alice).approve(await pair.getAddress(), amountB);

      const tx = await pair.connect(alice).addLiquidity(amountA, amountB);
      const receipt = await tx.wait();

      // sqrt(10000e18 * 10000e18) = 10000e18
      const expectedLP = hre.ethers.parseEther("10000");

      // Check via event
      const event = receipt.logs.find((log) => {
        try {
          return pair.interface.parseLog(log)?.name === "LiquidityAdded";
        } catch {
          return false;
        }
      });
      expect(event).to.not.be.undefined;
      const parsed = pair.interface.parseLog(event);
      expect(parsed.args.liquidity).to.equal(expectedLP);
    });

    it("subsequent provider receives proportional LP tokens", async function () {
      const amountA = hre.ethers.parseEther("10000");
      const amountB = hre.ethers.parseEther("10000");

      // Alice adds first liquidity
      await tokenA.connect(alice).approve(await pair.getAddress(), amountA);
      await tokenB.connect(alice).approve(await pair.getAddress(), amountB);
      await pair.connect(alice).addLiquidity(amountA, amountB);

      // Bob adds half the amount
      const halfA = hre.ethers.parseEther("5000");
      const halfB = hre.ethers.parseEther("5000");
      await tokenA.connect(bob).approve(await pair.getAddress(), halfA);
      await tokenB.connect(bob).approve(await pair.getAddress(), halfB);

      const tx = await pair.connect(bob).addLiquidity(halfA, halfB);
      const receipt = await tx.wait();

      // Should get 5000e18 LP tokens (half of Alice's 10000e18)
      const expectedLP = hre.ethers.parseEther("5000");
      const event = receipt.logs.find((log) => {
        try {
          return pair.interface.parseLog(log)?.name === "LiquidityAdded";
        } catch {
          return false;
        }
      });
      const parsed = pair.interface.parseLog(event);
      expect(parsed.args.liquidity).to.equal(expectedLP);
    });

    it("reverts when amount is zero", async function () {
      const amount = hre.ethers.parseEther("10000");
      await tokenA.connect(alice).approve(await pair.getAddress(), amount);
      await tokenB.connect(alice).approve(await pair.getAddress(), amount);

      await expect(
        pair.connect(alice).addLiquidity(0, amount)
      ).to.be.reverted;

      await expect(
        pair.connect(alice).addLiquidity(amount, 0)
      ).to.be.reverted;
    });
  });

  describe("getReserves", function () {
    it("returns zero reserves initially", async function () {
      const [rA, rB] = await pair.getReserves();
      expect(rA).to.equal(0);
      expect(rB).to.equal(0);
    });

    it("returns correct reserves after addLiquidity", async function () {
      const amountA = hre.ethers.parseEther("10000");
      const amountB = hre.ethers.parseEther("20000");

      await tokenA.connect(alice).approve(await pair.getAddress(), amountA);
      await tokenB.connect(alice).approve(await pair.getAddress(), amountB);
      await pair.connect(alice).addLiquidity(amountA, amountB);

      const [rA, rB] = await pair.getReserves();
      expect(rA).to.equal(amountA);
      expect(rB).to.equal(amountB);
    });
  });

  describe("swap", function () {
    beforeEach(async function () {
      // Alice provides initial liquidity: 10000 of each
      const amountA = hre.ethers.parseEther("10000");
      const amountB = hre.ethers.parseEther("10000");

      await tokenA.connect(alice).approve(await pair.getAddress(), amountA);
      await tokenB.connect(alice).approve(await pair.getAddress(), amountB);
      await pair.connect(alice).addLiquidity(amountA, amountB);
    });

    it("swaps with correct output using 0.3% fee", async function () {
      const swapIn = hre.ethers.parseEther("100");

      await tokenA.connect(bob).approve(await pair.getAddress(), swapIn);
      const tx = await pair
        .connect(bob)
        .swap(await tokenA.getAddress(), swapIn);
      const receipt = await tx.wait();

      // Expected output:
      // amountOut = (10000e18 * 100e18 * 997) / (10000e18 * 1000 + 100e18 * 997)
      //           = (997000000e36) / (10099700e18)
      //           ~= 98715...e18  (approximately 98.715 tokens)
      const reserveIn = hre.ethers.parseEther("10000");
      const reserveOut = hre.ethers.parseEther("10000");
      const amountInWithFee = swapIn * 997n;
      const numerator = reserveOut * amountInWithFee;
      const denominator = reserveIn * 1000n + amountInWithFee;
      const expectedOut = numerator / denominator;

      const event = receipt.logs.find((log) => {
        try {
          return pair.interface.parseLog(log)?.name === "Swap";
        } catch {
          return false;
        }
      });
      const parsed = pair.interface.parseLog(event);
      expect(parsed.args.amountOut).to.equal(expectedOut);
    });

    it("updates reserves after swap", async function () {
      const swapIn = hre.ethers.parseEther("100");
      await tokenA.connect(bob).approve(await pair.getAddress(), swapIn);
      await pair.connect(bob).swap(await tokenA.getAddress(), swapIn);

      const [rA, rB] = await pair.getReserves();
      // reserveA increased, reserveB decreased
      expect(rA).to.be.gt(hre.ethers.parseEther("10000"));
      expect(rB).to.be.lt(hre.ethers.parseEther("10000"));
    });

    it("reverts if tokenIn is not tokenA or tokenB", async function () {
      const swapIn = hre.ethers.parseEther("100");
      const fakeToken = bob.address; // not a valid pair token
      await expect(
        pair.connect(bob).swap(fakeToken, swapIn)
      ).to.be.reverted;
    });

    it("reverts if pool has no liquidity", async function () {
      // Deploy a fresh pair with no liquidity
      const SimplePair = await hre.ethers.getContractFactory("SimplePair");
      const emptyPair = await SimplePair.deploy(
        await tokenA.getAddress(),
        await tokenB.getAddress()
      );
      await emptyPair.waitForDeployment();

      const swapIn = hre.ethers.parseEther("100");
      await tokenA.connect(bob).approve(await emptyPair.getAddress(), swapIn);
      await expect(
        emptyPair.connect(bob).swap(await tokenA.getAddress(), swapIn)
      ).to.be.reverted;
    });
  });

  describe("removeLiquidity", function () {
    it("returns proportional share of reserves", async function () {
      const amountA = hre.ethers.parseEther("10000");
      const amountB = hre.ethers.parseEther("10000");

      // Alice adds liquidity
      await tokenA.connect(alice).approve(await pair.getAddress(), amountA);
      await tokenB.connect(alice).approve(await pair.getAddress(), amountB);
      const tx = await pair.connect(alice).addLiquidity(amountA, amountB);
      const receipt = await tx.wait();

      // Get LP tokens minted
      const event = receipt.logs.find((log) => {
        try {
          return pair.interface.parseLog(log)?.name === "LiquidityAdded";
        } catch {
          return false;
        }
      });
      const lpTokens = pair.interface.parseLog(event).args.liquidity;

      // Track alice's tokenA balance before removal
      const balBefore = await tokenA.balanceOf(alice.address);

      // Remove all liquidity
      const removeTx = await pair.connect(alice).removeLiquidity(lpTokens);
      const removeReceipt = await removeTx.wait();

      const removeEvent = removeReceipt.logs.find((log) => {
        try {
          return pair.interface.parseLog(log)?.name === "LiquidityRemoved";
        } catch {
          return false;
        }
      });
      const parsed = pair.interface.parseLog(removeEvent);

      // Should get back the full amounts (all liquidity removed)
      expect(parsed.args.amountA).to.equal(amountA);
      expect(parsed.args.amountB).to.equal(amountB);

      // Reserves should be zero
      const [rA, rB] = await pair.getReserves();
      expect(rA).to.equal(0);
      expect(rB).to.equal(0);
    });

    it("returns partial share when removing partial liquidity", async function () {
      const amountA = hre.ethers.parseEther("10000");
      const amountB = hre.ethers.parseEther("10000");

      await tokenA.connect(alice).approve(await pair.getAddress(), amountA);
      await tokenB.connect(alice).approve(await pair.getAddress(), amountB);
      const tx = await pair.connect(alice).addLiquidity(amountA, amountB);
      const receipt = await tx.wait();

      const event = receipt.logs.find((log) => {
        try {
          return pair.interface.parseLog(log)?.name === "LiquidityAdded";
        } catch {
          return false;
        }
      });
      const lpTokens = pair.interface.parseLog(event).args.liquidity;

      // Remove half
      const halfLP = lpTokens / 2n;
      const removeTx = await pair.connect(alice).removeLiquidity(halfLP);
      const removeReceipt = await removeTx.wait();

      const removeEvent = removeReceipt.logs.find((log) => {
        try {
          return pair.interface.parseLog(log)?.name === "LiquidityRemoved";
        } catch {
          return false;
        }
      });
      const parsed = pair.interface.parseLog(removeEvent);

      expect(parsed.args.amountA).to.equal(amountA / 2n);
      expect(parsed.args.amountB).to.equal(amountB / 2n);

      // Half reserves remain
      const [rA, rB] = await pair.getReserves();
      expect(rA).to.equal(amountA / 2n);
      expect(rB).to.equal(amountB / 2n);
    });

    it("reverts if user has insufficient LP tokens", async function () {
      const amountA = hre.ethers.parseEther("10000");
      const amountB = hre.ethers.parseEther("10000");

      await tokenA.connect(alice).approve(await pair.getAddress(), amountA);
      await tokenB.connect(alice).approve(await pair.getAddress(), amountB);
      await pair.connect(alice).addLiquidity(amountA, amountB);

      // Bob has no LP tokens
      await expect(
        pair.connect(bob).removeLiquidity(hre.ethers.parseEther("1"))
      ).to.be.reverted;
    });
  });
});
