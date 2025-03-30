// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

interface IPancakeRouter {
    function swapExactTokensForTokens(
        uint amountIn,
        uint amountOutMin,
        address[] calldata path,
        address to,
        uint deadline
    ) external returns (uint[] memory amounts);

    function getAmountsOut(
        uint amountIn,
        address[] calldata path
    ) external view returns (uint[] memory amounts);
}

contract TokenSwapper is Ownable {
    // BSC测试网上的PancakeSwap路由器地址
    address public immutable pancakeRouterAddress;
    IPancakeRouter public immutable pancakeRouter;

    event TokensSwapped(
        address indexed user,
        address indexed tokenA,
        uint256 amountA,
        address indexed tokenB,
        uint256 amountB
    );

    constructor(address _pancakeRouterAddress) Ownable(msg.sender) {
        pancakeRouterAddress = _pancakeRouterAddress;
        pancakeRouter = IPancakeRouter(_pancakeRouterAddress);
    }

    // 查询可以获得的tokenB数量
    function getEstimatedTokenBAmount(
        address tokenA,
        address tokenB,
        uint256 amountA
    ) external view returns (uint256) {
        address[] memory path = new address[](2);
        path[0] = tokenA;
        path[1] = tokenB;

        uint[] memory amounts = pancakeRouter.getAmountsOut(amountA, path);
        return amounts[1];
    }

    // 主要交换功能
    function swapTokens(
        address tokenA,
        address tokenB,
        uint256 amountA
    ) external {
        // 确保用户已授权合约使用tokenA
        IERC20(tokenA).transferFrom(msg.sender, address(this), amountA);

        // 授权路由器使用合约中的tokenA
        IERC20(tokenA).approve(pancakeRouterAddress, amountA);

        // 设置交换路径
        address[] memory path = new address[](2);
        path[0] = tokenA;
        path[1] = tokenB;

        // 计算最小获得的tokenB数量（接受1%的滑点）
        uint[] memory amountsOut = pancakeRouter.getAmountsOut(amountA, path);
        uint minAmountOut = (amountsOut[1] * 99) / 100; // 99% of expected output

        // 执行代币交换
        uint[] memory amounts = pancakeRouter.swapExactTokensForTokens(
            amountA,
            minAmountOut,
            path,
            msg.sender, // 直接发送到用户地址
            block.timestamp + 300 // 5分钟过期时间
        );

        // 触发事件
        emit TokensSwapped(msg.sender, tokenA, amountA, tokenB, amounts[1]);
    }

    // 紧急提款函数（以防有代币被卡在合约中）
    function rescueTokens(address token, uint256 amount) external onlyOwner {
        IERC20(token).transfer(owner(), amount);
    }
}
