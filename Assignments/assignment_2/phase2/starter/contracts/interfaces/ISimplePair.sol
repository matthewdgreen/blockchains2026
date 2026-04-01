// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/// @title ISimplePair - Simplified Uniswap V2 Pair Interface
/// @notice Implement a constant-product AMM (x * y = k) for two ERC20 tokens.
///         Your contract will be initialized with two token addresses and must support
///         adding/removing liquidity and swapping tokens.
/// @dev Key concepts:
///   - The pair holds reserves of both tokens
///   - LP tokens track each provider's share of the pool
///   - Swaps use the constant product formula with a 0.3% fee
///   - Users must approve() tokens to the pair contract before calling addLiquidity/swap
interface ISimplePair {
    /// @notice Add liquidity to the pool
    /// @param amountA Amount of tokenA to deposit
    /// @param amountB Amount of tokenB to deposit
    /// @return liquidity The amount of LP tokens minted
    /// @dev First provider: liquidity = sqrt(amountA * amountB)
    ///      Subsequent: liquidity = min(amountA * totalLP / reserveA, amountB * totalLP / reserveB)
    ///      Must transfer tokens from msg.sender (requires prior approval)
    ///      Both amounts must be > 0
    function addLiquidity(uint256 amountA, uint256 amountB) external returns (uint256 liquidity);

    /// @notice Remove liquidity from the pool
    /// @param liquidity Amount of LP tokens to burn
    /// @return amountA Amount of tokenA returned
    /// @return amountB Amount of tokenB returned
    /// @dev amountA = liquidity * reserveA / totalLP
    ///      amountB = liquidity * reserveB / totalLP
    ///      Must have sufficient LP token balance
    function removeLiquidity(uint256 liquidity) external returns (uint256 amountA, uint256 amountB);

    /// @notice Swap one token for the other
    /// @param tokenIn Address of the token being sold (must be tokenA or tokenB)
    /// @param amountIn Amount of tokenIn to sell
    /// @return amountOut Amount of the other token received
    /// @dev Uses constant product formula with 0.3% fee:
    ///      amountOut = (reserveOut * amountIn * 997) / (reserveIn * 1000 + amountIn * 997)
    ///      Must transfer tokenIn from msg.sender (requires prior approval)
    function swap(address tokenIn, uint256 amountIn) external returns (uint256 amountOut);

    /// @notice Get current reserves
    /// @return reserveA Current reserve of tokenA
    /// @return reserveB Current reserve of tokenB
    function getReserves() external view returns (uint256 reserveA, uint256 reserveB);

    /// @notice Get the address of tokenA
    function tokenA() external view returns (address);

    /// @notice Get the address of tokenB
    function tokenB() external view returns (address);

    // Events
    event LiquidityAdded(address indexed provider, uint256 amountA, uint256 amountB, uint256 liquidity);
    event LiquidityRemoved(address indexed provider, uint256 amountA, uint256 amountB, uint256 liquidity);
    event Swap(address indexed user, address indexed tokenIn, uint256 amountIn, uint256 amountOut);
}
