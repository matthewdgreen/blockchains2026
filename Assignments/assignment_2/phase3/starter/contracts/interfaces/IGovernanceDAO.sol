// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/// @title IGovernanceDAO - Governance contract interface
/// @notice A delegation-based governance contract where token holders delegate
///         voting power, create proposals, vote, and execute.
/// @dev The DAO uses the GOV token for voting power. When you call delegate(),
///      your current token balance is recorded as voting power for the delegatee.
///      Proposals that reach quorum can be executed immediately.
interface IGovernanceDAO {
    /// @notice Delegate your voting power to another address (or yourself)
    /// @param delegatee The address to receive your voting power
    /// @dev Your current governanceToken.balanceOf(msg.sender) is recorded
    ///      as voting power for the delegatee. You can only delegate once.
    function delegate(address delegatee) external;

    /// @notice Create a new governance proposal
    /// @param description Human-readable description of the proposal
    /// @param target The contract address to call if the proposal passes
    /// @param data The calldata to execute on the target contract
    /// @return proposalId The ID of the newly created proposal
    /// @dev Requires the caller to have voting power (must delegate first)
    function propose(
        string calldata description,
        address target,
        bytes calldata data
    ) external returns (uint256 proposalId);

    /// @notice Vote in favor of a proposal
    /// @param proposalId The proposal to vote on
    /// @dev Uses your delegated voting power. Can only vote once per proposal.
    function vote(uint256 proposalId) external;

    /// @notice Execute a proposal that has reached quorum
    /// @param proposalId The proposal to execute
    /// @dev Calls target.call(data) from the original proposal.
    ///      Reverts if quorum is not reached or proposal was already executed.
    function execute(uint256 proposalId) external;

    /// @notice Change the TA address. Only callable via governance.
    /// @param newTA The new TA address
    function setTA(address newTA) external;

    /// @notice Set a student's grade. Only callable by the current TA.
    /// @param student The student's address
    /// @param grade The grade to assign
    function setGrade(address student, uint256 grade) external;

    /// @notice Get the current TA address
    function ta() external view returns (address);

    /// @notice Get the quorum threshold
    function quorum() external view returns (uint256);

    /// @notice Get the delegated voting power of an address
    function votingPower(address account) external view returns (uint256);

    /// @notice Check if an address has already delegated
    function hasDelegated(address account) external view returns (bool);

    /// @notice Get a student's grade
    function grades(address student) external view returns (uint256);

    /// @notice Get the total number of proposals
    function proposalCount() external view returns (uint256);

    /// @notice Get the governance token address
    function governanceToken() external view returns (address);
}
