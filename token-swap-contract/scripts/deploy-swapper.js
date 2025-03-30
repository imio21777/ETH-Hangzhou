const hre = require("hardhat");

async function main() {
  const [deployer] = await hre.ethers.getSigners();
  console.log("使用账户部署:", deployer.address);

  // BSC测试网上的PancakeSwap路由器地址
  const PANCAKE_ROUTER_TESTNET = "0xD99D1c33F9fC3444f8101754aBC46c52416550D1";

  // 部署交换合约
  const TokenSwapper = await hre.ethers.getContractFactory("TokenSwapper");
  const tokenSwapper = await TokenSwapper.deploy(PANCAKE_ROUTER_TESTNET);

  await tokenSwapper.waitForDeployment();

  const swapperAddress = await tokenSwapper.getAddress();
  console.log(`TokenSwapper部署成功！地址: ${swapperAddress}`);
  console.log(`PancakeSwap路由器地址: ${PANCAKE_ROUTER_TESTNET}`);
  console.log("");
  console.log("验证合约指令:");
  console.log(
    `npx hardhat verify --network bscTestnet ${swapperAddress} ${PANCAKE_ROUTER_TESTNET}`
  );
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
