// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

/// @title GovernanceToken - Included for local testing only
/// @dev On Sepolia, the TA has already deployed this contract.
contract GovernanceToken is ERC20, Ownable {
    uint256 public constant INITIAL_SUPPLY = 10_000_000 * 10 ** 18;

    constructor() ERC20("Governance Token", "GOV") Ownable(msg.sender) {
        _mint(msg.sender, INITIAL_SUPPLY);
    }

    function batchTransfer(
        address[] calldata recipients,
        uint256 amount
    ) external onlyOwner {
        for (uint256 i = 0; i < recipients.length; i++) {
            _transfer(msg.sender, recipients[i], amount);
        }
    }
}
