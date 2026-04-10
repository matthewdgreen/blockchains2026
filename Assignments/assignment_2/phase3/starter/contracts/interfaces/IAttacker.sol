// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/// @title IAttacker - Interface your exploit contract must implement
/// @notice Your contract must expose these two functions. The test suite
///         and deploy script will call attack() to trigger your exploit.
interface IAttacker {
    /// @notice Entry point for your exploit. Must complete in a single transaction.
    function attack() external;

    /// @notice Callback invoked by LendingPool during a flash loan.
    ///         You must repay the full loan amount before this function returns.
    /// @param amount The amount of tokens borrowed
    function onFlashLoan(uint256 amount) external;
}
