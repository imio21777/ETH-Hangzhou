const hre = require("hardhat");

async function main() {
  // 配置参数

  //! here is swapper contract addr
  const SWAPPER_ADDRESS = "0xF6FB382D0B6086093bEe37d01230fa51D2b9a567";
  const TOKEN_A_ADDRESS = "0x8Fd7e4A68deE8F92Ef92bEC58b369C3e926141Aa";
  const TOKEN_B_ADDRESS = "0x5BBae9C6741e31A1C0088334be84e6c09598c027";
  const AMOUNT_TO_SWAP = hre.ethers.parseUnits("10", 18); // 交换10个TokenA

  // 获取签名者
  const [owner] = await hre.ethers.getSigners();
  console.log("使用账户:", owner.address);

  // 获取合约实例
  const TokenA = await hre.ethers.getContractAt("TestToken", TOKEN_A_ADDRESS);
  const TokenB = await hre.ethers.getContractAt("TestToken", TOKEN_B_ADDRESS);
  const Swapper = await hre.ethers.getContractAt(
    "TokenSwapper",
    SWAPPER_ADDRESS
  );

  // 获取初始余额
  const initialBalanceA = await TokenA.balanceOf(owner.address);
  const initialBalanceB = await TokenB.balanceOf(owner.address);
  console.log("初始TokenA余额:", hre.ethers.formatUnits(initialBalanceA, 18));
  console.log("初始TokenB余额:", hre.ethers.formatUnits(initialBalanceB, 18));

  // 添加这些代码在调用getEstimatedTokenBAmount之前
  console.log("Swapper地址:", SWAPPER_ADDRESS);
  console.log("TokenA地址:", TOKEN_A_ADDRESS);
  console.log("TokenB地址:", TOKEN_B_ADDRESS);
  console.log("交换数量:", AMOUNT_TO_SWAP.toString());

  try {
    // 尝试获取预估交换数量
    const estimatedB = await Swapper.getEstimatedTokenBAmount(
      TOKEN_A_ADDRESS,
      TOKEN_B_ADDRESS,
      AMOUNT_TO_SWAP
    );
    console.log("预计获得TokenB数量:", hre.ethers.formatUnits(estimatedB, 18));
  } catch (error) {
    console.error("获取预估值失败:", error.message);
    // 继续执行其他代码...
  }

  // 授权合约使用TokenA
  console.log("正在授权TokenA...");
  const approveTx = await TokenA.approve(SWAPPER_ADDRESS, AMOUNT_TO_SWAP);
  await approveTx.wait();
  console.log("授权成功");

  // 执行代币交换
  console.log("正在交换代币...");
  try {
    const swapTx = await Swapper.swapTokens(
      TOKEN_A_ADDRESS,
      TOKEN_B_ADDRESS,
      AMOUNT_TO_SWAP
    );
    const receipt = await swapTx.wait();
    console.log("交换成功，交易哈希:", receipt.hash);
  } catch (error) {
    console.error("交换失败:", error.message);
    // 继续执行其他代码...
  }

  // 获取交换后余额
  const finalBalanceA = await TokenA.balanceOf(owner.address);
  const finalBalanceB = await TokenB.balanceOf(owner.address);
  console.log("交换后TokenA余额:", hre.ethers.formatUnits(finalBalanceA, 18));
  console.log("交换后TokenB余额:", hre.ethers.formatUnits(finalBalanceB, 18));

  // 计算变化
  const changeA = initialBalanceA - finalBalanceA;
  const changeB = finalBalanceB - initialBalanceB;
  console.log("TokenA减少:", hre.ethers.formatUnits(changeA, 18));
  console.log("TokenB增加:", hre.ethers.formatUnits(changeB, 18));
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
