// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";

/// @title GovernanceDAO - A governance contract with a critical vulnerability
/// @notice This contract contains a bug. Find it and exploit it.
/// @dev On Sepolia, the TA has already deployed this contract.
contract GovernanceDAO {
    IERC20 public immutable governanceToken;

    address public ta;
    uint256 public quorum;

    mapping(address => uint256) public votingPower;
    mapping(address => bool) public hasDelegated;

    struct Proposal {
        address proposer;
        string description;
        address target;
        bytes data;
        uint256 votesFor;
        bool executed;
    }

    uint256 public proposalCount;
    mapping(uint256 => Proposal) public proposals;
    mapping(uint256 => mapping(address => bool)) public hasVoted;

    mapping(address => uint256) public grades;

    event Delegated(address indexed delegator, address indexed delegatee, uint256 power);
    event ProposalCreated(uint256 indexed proposalId, address indexed proposer, string description);
    event Voted(uint256 indexed proposalId, address indexed voter, uint256 power);
    event ProposalExecuted(uint256 indexed proposalId);
    event GradeSet(address indexed student, uint256 grade);
    event TAChanged(address indexed oldTA, address indexed newTA);

    constructor(address _governanceToken, uint256 _quorum) {
        governanceToken = IERC20(_governanceToken);
        ta = msg.sender;
        quorum = _quorum;
    }

    function delegate(address delegatee) external {
        require(!hasDelegated[msg.sender], "Already delegated");
        uint256 power = governanceToken.balanceOf(msg.sender);
        require(power > 0, "No tokens to delegate");

        hasDelegated[msg.sender] = true;
        votingPower[delegatee] += power;

        emit Delegated(msg.sender, delegatee, power);
    }

    function propose(
        string calldata description,
        address target,
        bytes calldata data
    ) external returns (uint256 proposalId) {
        require(votingPower[msg.sender] > 0, "No voting power");

        proposalId = proposalCount++;
        Proposal storage p = proposals[proposalId];
        p.proposer = msg.sender;
        p.description = description;
        p.target = target;
        p.data = data;

        emit ProposalCreated(proposalId, msg.sender, description);
    }

    function vote(uint256 proposalId) external {
        require(proposalId < proposalCount, "Invalid proposal");
        Proposal storage p = proposals[proposalId];
        require(!p.executed, "Already executed");
        require(!hasVoted[proposalId][msg.sender], "Already voted");
        require(votingPower[msg.sender] > 0, "No voting power");

        hasVoted[proposalId][msg.sender] = true;
        p.votesFor += votingPower[msg.sender];

        emit Voted(proposalId, msg.sender, votingPower[msg.sender]);
    }

    function execute(uint256 proposalId) external {
        require(proposalId < proposalCount, "Invalid proposal");
        Proposal storage p = proposals[proposalId];
        require(!p.executed, "Already executed");
        require(p.votesFor >= quorum, "Quorum not reached");

        p.executed = true;

        (bool success, ) = p.target.call(p.data);
        require(success, "Execution failed");

        emit ProposalExecuted(proposalId);
    }

    function setTA(address newTA) external {
        require(msg.sender == address(this), "Only via governance");
        emit TAChanged(ta, newTA);
        ta = newTA;
    }

    function setGrade(address student, uint256 grade) external {
        require(msg.sender == ta, "Only TA");
        require(grade <= 100, "Grade must be 0-100");
        grades[student] = grade;
        emit GradeSet(student, grade);
    }
}
