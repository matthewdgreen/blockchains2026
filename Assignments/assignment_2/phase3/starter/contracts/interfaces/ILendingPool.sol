// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/// @title IFlashLoanReceiver - Callback interface for flash loan recipients
/// @notice Implement this interface in your contract to receive flash loans.
///         Your onFlashLoan function will be called after tokens are transferred to you.
///         You MUST repay the full loan amount before onFlashLoan returns.
interface IFlashLoanReceiver {
    /// @notice Called by LendingPool after transferring borrowed tokens
    /// @param amount The amount of tokens borrowed
    function onFlashLoan(uint256 amount) external;
}

/// @title ILendingPool - Flash loan provider interface
/// @notice The LendingPool holds GOV tokens and offers zero-fee flash loans.
///         Borrowers must implement IFlashLoanReceiver and repay within the same transaction.
interface ILendingPool {
    /// @notice The ERC20 token available for flash loans
    function token() external view returns (address);

    /// @notice Borrow tokens via flash loan
    /// @param amount The number of tokens to borrow
    /// @dev After calling this, the LendingPool will:
    ///   1. Transfer `amount` tokens to msg.sender
    ///   2. Call msg.sender.onFlashLoan(amount)
    ///   3. Verify that its token balance is >= what it was before the loan
    ///   If the balance check fails, the entire transaction reverts.
    function flashLoan(uint256 amount) external;
}
