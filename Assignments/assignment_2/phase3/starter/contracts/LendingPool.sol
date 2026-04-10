// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "./interfaces/ILendingPool.sol";

/// @title LendingPool - Included for local testing only
/// @dev On Sepolia, the TA has already deployed this contract.
contract LendingPool {
    IERC20 public immutable token;

    event FlashLoan(address indexed borrower, uint256 amount);

    constructor(address _token) {
        token = IERC20(_token);
    }

    function flashLoan(uint256 amount) external {
        uint256 balanceBefore = token.balanceOf(address(this));
        require(balanceBefore >= amount, "Insufficient liquidity");

        token.transfer(msg.sender, amount);

        IFlashLoanReceiver(msg.sender).onFlashLoan(amount);

        require(
            token.balanceOf(address(this)) >= balanceBefore,
            "Flash loan not repaid"
        );

        emit FlashLoan(msg.sender, amount);
    }
}
