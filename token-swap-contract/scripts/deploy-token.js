const hre = require("hardhat");

async function main() {
  const [deployer] = await hre.ethers.getSigners();
  console.log("使用账户部署:", deployer.address);

  // 代币参数
  const tokenName = "Token A";
  const tokenSymbol = "TKA";
  const initialSupply = 1000000000; // 初始供应量（百万）

  // 部署代币合约
  const MyToken = await hre.ethers.getContractFactory("TestToken");
  const myToken = await MyToken.deploy(tokenName, tokenSymbol, initialSupply);

  await myToken.waitForDeployment();

  const tokenAddress = await myToken.getAddress();
  console.log(`代币部署成功！地址: ${tokenAddress}`);
  console.log(`代币名称: ${tokenName}`);
  console.log(`代币符号: ${tokenSymbol}`);
  console.log(`初始供应量: ${initialSupply}`);
  console.log("");
  console.log("验证合约指令:");
  console.log(
    `npx hardhat verify --network bscTestnet ${tokenAddress} "${tokenName}" "${tokenSymbol}" ${initialSupply}`
  );
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
