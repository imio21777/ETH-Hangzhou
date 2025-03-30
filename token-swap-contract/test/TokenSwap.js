// const { expect } = require("chai");
// const { ethers } = require("hardhat");

// describe("TokenSwap", function () {
//   let tokenSwap, owner, user;
//   const PANCAKE_ROUTER_ADDRESS = "0x10ED43C718714eb63d5aA57B78B54704E256024E"; // BSC主网地址
//   const USDT_ADDRESS = "0x55d398326f99059fF775485246999027B3197955"; // BSC上的USDT
//   const BUSD_ADDRESS = "0xe9e7CEA3DedcA5984780Bafc599bD69ADd087D56"; // BUSD

//   beforeEach(async function () {
//     [owner, user] = await ethers.getSigners();

//     const TokenSwap = await ethers.getContractFactory("TokenSwap");
//     tokenSwap = await TokenSwap.deploy(PANCAKE_ROUTER_ADDRESS);
//     await tokenSwap.waitForDeployment();
//   });

//   it("应该能够获取代币兑换估值", async function () {
//     // 注意：此测试需要连接到分叉的主网或测试网络
//     // 这只是一个示例，实际运行时可能需要调整
//     const amountA = ethers.parseUnits("100", 18); // 100 USDT

//     const estimatedAmount = await tokenSwap.getEstimatedTokenBAmount(
//       USDT_ADDRESS,
//       BUSD_ADDRESS,
//       amountA
//     );

//     expect(estimatedAmount).to.be.gt(0);
//   });

//   // 更多测试...
// });

const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("TokenSwap", function () {
  let tokenSwap, mockRouter, tokenA, tokenB, owner, user;

  beforeEach(async function () {
    [owner, user] = await ethers.getSigners();

    // 部署模拟路由器
    const MockRouter = await ethers.getContractFactory("MockPancakeRouter");
    mockRouter = await MockRouter.deploy();

    // 部署测试代币
    const TestToken = await ethers.getContractFactory("TestToken");
    tokenA = await TestToken.deploy("Test USDT", "TUSDT");
    tokenB = await TestToken.deploy("Test BUSD", "TBUSD");

    // 部署TokenSwap合约
    const TokenSwap = await ethers.getContractFactory("TokenSwap");
    tokenSwap = await TokenSwap.deploy(await mockRouter.getAddress());
  });

  it("应该能够获取代币兑换估值", async function () {
    const amountA = ethers.parseUnits("100", 18);
    const tokenAAddress = await tokenA.getAddress();
    const tokenBAddress = await tokenB.getAddress();

    const estimatedAmount = await tokenSwap.getEstimatedTokenBAmount(
      tokenAAddress,
      tokenBAddress,
      amountA
    );

    expect(estimatedAmount).to.equal((amountA * 9n) / 10n);
  });
});
