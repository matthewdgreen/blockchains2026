// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";

/**
 * @title StudentToken
 * @notice Your custom ERC20 token for the Blockchains 2026 course.
 *
 * Requirements:
 *   - Must inherit from OpenZeppelin's ERC20
 *   - Must have a non-empty name and symbol
 *   - totalSupply must be >= 1,000,000 * 10**18 after deployment
 *   - The deployer must hold tokens after deployment
 *   - Must pass all checks in the course Registry contract
 *
 * See: https://docs.openzeppelin.com/contracts/5.x/erc20
 */
contract StudentToken is ERC20 {

    constructor()
        ERC20("TODO", "TODO")
    {
        // TODO: mint tokens to the deployer
    }
}
