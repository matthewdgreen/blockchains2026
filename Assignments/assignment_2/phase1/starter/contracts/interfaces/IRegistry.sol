// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/// @title IRegistry - Course Registration Interface
/// @notice Interface for the course Registry contract deployed by the TA on Sepolia.
/// @dev Students use this interface to interact with the Registry.
///      The Registry validates your ERC20 token and stores your name commitment.
interface IRegistry {
    struct StudentInfo {
        address student;
        address token;
        bytes32 nameHash;
        bool approved;
        uint256 registeredAt;
    }

    /// @notice Minimum total supply required for student tokens (1,000,000 * 10^18)
    function MIN_SUPPLY() external view returns (uint256);

    /// @notice Register as a student with your ERC20 token
    /// @param tokenAddress Your deployed ERC20 token contract address
    /// @param nameHash keccak256(abi.encodePacked(yourRealName, yourSecret)) where yourSecret is a uint256
    /// @dev Requirements:
    ///   - tokenAddress must be a deployed contract
    ///   - Token must implement ERC20 (name, symbol, totalSupply, balanceOf, transfer)
    ///   - Token totalSupply must be >= MIN_SUPPLY
    ///   - You must hold tokens (balanceOf(msg.sender) > 0)
    ///   - Each student can only register once
    ///   - Each token can only be registered once
    function registerStudent(address tokenAddress, bytes32 nameHash) external;

    /// @notice Check if a student has been approved by the TA
    function isApproved(address student) external view returns (bool);

    /// @notice Check if a student is registered
    function isRegistered(address student) external view returns (bool);

    /// @notice Get the token address for a registered student
    function getToken(address student) external view returns (address);

    /// @notice Get full registration info for a student
    function getStudentInfo(address student) external view returns (StudentInfo memory);
}
