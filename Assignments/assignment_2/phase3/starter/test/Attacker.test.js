const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("Phase 3: Flash Loan Exploit", function () {
  let governanceToken, lendingPool, dao, attacker;
  let deployer, student;

  const INITIAL_SUPPLY = ethers.parseEther("10000000"); // 10M GOV
  const POOL_AMOUNT = ethers.parseEther("5000000"); // 5M GOV in lending pool
  const STUDENT_AIRDROP = ethers.parseEther("1000"); // 1000 GOV per student
  const QUORUM = ethers.parseEther("1000000"); // 1M votes needed

  beforeEach(async function () {
    [deployer, student] = await ethers.getSigners();

    // --- TA setup (simulates what's already deployed on Sepolia) ---

    // Deploy GOV token
    const GovernanceToken = await ethers.getContractFactory("GovernanceToken");
    governanceToken = await GovernanceToken.deploy();

    // Deploy and fund LendingPool
    const LendingPool = await ethers.getContractFactory("LendingPool");
    lendingPool = await LendingPool.deploy(governanceToken.target);
    await governanceToken.transfer(lendingPool.target, POOL_AMOUNT);

    // Deploy GovernanceDAO
    const GovernanceDAO = await ethers.getContractFactory("GovernanceDAO");
    dao = await GovernanceDAO.deploy(governanceToken.target, QUORUM);

    // Airdrop to student
    await governanceToken.transfer(student.address, STUDENT_AIRDROP);

    // --- Student deploys their Attacker contract ---
    const Attacker = await ethers.getContractFactory("Attacker");
    attacker = await Attacker.connect(student).deploy(
      lendingPool.target,
      dao.target,
      governanceToken.target
    );
  });

  it("should make the student the new TA", async function () {
    await attacker.connect(student).attack();
    expect(await dao.ta()).to.equal(student.address);
  });

  it("should set the student's grade to a value between 1 and 100", async function () {
    await attacker.connect(student).attack();
    const grade = await dao.grades(student.address);
    expect(grade).to.be.gte(1);
    expect(grade).to.be.lte(100);
  });

  it("should not drain the lending pool", async function () {
    const before = await governanceToken.balanceOf(lendingPool.target);
    await attacker.connect(student).attack();
    const after = await governanceToken.balanceOf(lendingPool.target);
    expect(after).to.equal(before);
  });

  it("should complete in a single transaction", async function () {
    // The attack() call is one transaction — if it doesn't revert, it worked atomically
    const tx = await attacker.connect(student).attack();
    const receipt = await tx.wait();
    expect(receipt.status).to.equal(1);
    expect(await dao.ta()).to.equal(student.address);
    const grade = await dao.grades(student.address);
    expect(grade).to.be.gte(1);
    expect(grade).to.be.lte(100);
  });
});
