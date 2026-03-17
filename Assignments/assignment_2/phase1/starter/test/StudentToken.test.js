const { expect } = require("chai");
const hre = require("hardhat");

describe("StudentToken", function () {
  let token;
  let owner;

  beforeEach(async function () {
    [owner] = await hre.ethers.getSigners();
    const StudentToken = await hre.ethers.getContractFactory("StudentToken");
    token = await StudentToken.deploy();
    await token.waitForDeployment();
  });

  describe("Basic Requirements", function () {
    it("should have a non-empty name", async function () {
      const name = await token.name();
      expect(name).to.be.a("string");
      expect(name.length).to.be.greaterThan(0);
      expect(name).to.not.include("TODO");
      console.log(`    Token name: ${name}`);
    });

    it("should have a non-empty symbol", async function () {
      const symbol = await token.symbol();
      expect(symbol).to.be.a("string");
      expect(symbol.length).to.be.greaterThan(0);
      expect(symbol).to.not.include("TODO");
      console.log(`    Token symbol: ${symbol}`);
    });

    it("should have totalSupply >= 1,000,000 tokens", async function () {
      const totalSupply = await token.totalSupply();
      const minSupply = hre.ethers.parseEther("1000000");
      expect(totalSupply).to.be.gte(minSupply);
      console.log(`    Total supply: ${hre.ethers.formatEther(totalSupply)}`);
    });

    it("should have 18 decimals", async function () {
      const decimals = await token.decimals();
      expect(decimals).to.equal(18n);
    });

    it("should assign initial tokens to the deployer", async function () {
      const ownerBalance = await token.balanceOf(owner.address);
      expect(ownerBalance).to.be.greaterThan(0n);
      console.log(`    Deployer balance: ${hre.ethers.formatEther(ownerBalance)}`);
    });
  });

  describe("ERC20 Functionality", function () {
    it("should allow transfers", async function () {
      const [, recipient] = await hre.ethers.getSigners();
      const amount = hre.ethers.parseEther("100");
      await token.transfer(recipient.address, amount);
      expect(await token.balanceOf(recipient.address)).to.equal(amount);
    });

    it("should allow approve and transferFrom", async function () {
      const [, spender, recipient] = await hre.ethers.getSigners();
      const amount = hre.ethers.parseEther("100");

      await token.approve(spender.address, amount);
      expect(await token.allowance(owner.address, spender.address)).to.equal(amount);

      await token.connect(spender).transferFrom(owner.address, recipient.address, amount);
      expect(await token.balanceOf(recipient.address)).to.equal(amount);
    });

    it("should emit Transfer events", async function () {
      const [, recipient] = await hre.ethers.getSigners();
      const amount = hre.ethers.parseEther("100");
      await expect(token.transfer(recipient.address, amount))
        .to.emit(token, "Transfer")
        .withArgs(owner.address, recipient.address, amount);
    });
  });

  describe("Registry Compatibility Check", function () {
    it("should pass all Registry validation checks", async function () {
      const name = await token.name();
      const symbol = await token.symbol();
      const supply = await token.totalSupply();
      const balance = await token.balanceOf(owner.address);
      const minSupply = hre.ethers.parseEther("1000000");

      const checks = {
        "Name is non-empty": name.length > 0,
        "Symbol is non-empty": symbol.length > 0,
        "Supply >= 1,000,000": supply >= minSupply,
        "Deployer holds tokens": balance > 0n,
      };

      console.log("\n    === Registry Compatibility Report ===");
      for (const [check, passed] of Object.entries(checks)) {
        console.log(`    ${passed ? "PASS" : "FAIL"} ${check}`);
      }
      console.log("    =====================================\n");

      expect(name.length).to.be.greaterThan(0);
      expect(symbol.length).to.be.greaterThan(0);
      expect(supply).to.be.gte(minSupply);
      expect(balance).to.be.greaterThan(0n);
    });
  });
});
