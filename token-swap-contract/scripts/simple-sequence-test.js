// 简化版SequenceStorage合约交互脚本
const hre = require("hardhat");
const { ethers } = require("hardhat");

async function main() {
  try {
    // 1. 准备环境
    console.log("======== 连接合约 ========");
    const network = await ethers.provider.getNetwork();
    console.log(`连接到网络: ${network.name} (chainId: ${network.chainId})`);

    // 合约地址 - 替换为你的合约地址
    const contractAddress = "0xfBAc6Da7fb89bBE6bE14a1C6C88C7F0aF42b643c";

    // 获取签名者
    const [signer] = await ethers.getSigners();
    console.log(`使用账户: ${signer.address}`);

    // 连接到合约
    const SequenceStorage = await ethers.getContractFactory("SequenceStorage");
    const sequenceStorage = await SequenceStorage.attach(contractAddress);

    console.log(`成功连接到合约: ${contractAddress}`);

    // 2. 存储序列
    console.log("\n======== 存储新序列 ========");
    const testSequence = [10, 20, 30, 40, 50];
    console.log(`存储序列: [${testSequence}]`);

    const storeTx = await sequenceStorage.storeSequence(testSequence);
    console.log(`交易已提交 (${storeTx.hash})，等待确认...`);

    const storeReceipt = await storeTx.wait();
    console.log(`交易已确认，区块号: ${storeReceipt.blockNumber}`);

    // 从事件中获取序列ID
    const storeEvent = storeReceipt.logs[0];
    const storeDecodedEvent = sequenceStorage.interface.parseLog(storeEvent);
    const sequenceId = storeDecodedEvent.args.sequenceId;

    console.log(`序列已存储，序列ID: ${sequenceId}`);

    // 3. 获取序列信息
    console.log("\n======== 获取序列信息 ========");
    const [values, timestamp] = await sequenceStorage.getSequence(sequenceId);
    console.log(`序列ID: ${sequenceId}`);
    console.log(`序列值: [${values}]`);
    console.log(`存储时间戳: ${timestamp}`);
    console.log(`存储日期: ${new Date(timestamp * 1000).toLocaleString()}`);

    // 4. 验证正确的序列
    console.log("\n======== 验证正确的序列 ========");
    const correctResult = await sequenceStorage.verifySequence(
      sequenceId,
      testSequence
    );
    console.log(
      `验证结果: ${
        correctResult.toString() === ethers.MaxUint256.toString()
          ? "成功"
          : "失败"
      }`
    );

    // 5. 验证错误的序列
    console.log("\n======== 验证错误的序列 ========");
    const wrongSequence = [10, 25, 30, 40, 50];
    console.log(`错误序列: [${wrongSequence}]`);
    const wrongResult = await sequenceStorage.verifySequence(
      sequenceId,
      wrongSequence
    );
    console.log(`验证结果: 失败`);
    console.log(`不匹配索引: ${wrongResult}`);

    // 6. 触发验证事件
    console.log("\n======== 触发验证事件 ========");
    const verifyTx = await sequenceStorage.recordVerification(
      sequenceId,
      wrongSequence
    );
    console.log(`交易已提交 (${verifyTx.hash})，等待确认...`);

    const verifyReceipt = await verifyTx.wait();
    const verifyEvent = verifyReceipt.logs[0];
    const verifyDecodedEvent = sequenceStorage.interface.parseLog(verifyEvent);

    console.log(`验证事件已记录!`);
    console.log(
      `验证结果: ${verifyDecodedEvent.args.success ? "成功" : "失败"}`
    );
    console.log(`不匹配索引: ${verifyDecodedEvent.args.mismatchIndex}`);

    // 7. 获取用户存储的所有序列
    console.log("\n======== 获取用户的所有序列 ========");
    const sequenceIds = await sequenceStorage.getUserSequences(signer.address);
    console.log(`用户 ${signer.address} 存储的序列数量: ${sequenceIds.length}`);

    for (let i = 0; i < sequenceIds.length; i++) {
      console.log(`\n序列 ${i + 1}: ${sequenceIds[i]}`);
      try {
        const [seqValues, seqTimestamp] = await sequenceStorage.getSequence(
          sequenceIds[i]
        );
        console.log(`值: [${seqValues}]`);
        console.log(`时间: ${new Date(seqTimestamp * 1000).toLocaleString()}`);
      } catch (e) {
        console.log(`无法获取详情: ${e.message}`);
      }
    }

    console.log("\n======== 测试完成 ========");
  } catch (error) {
    console.error(`执行过程中出错: ${error.message}`);
    if (error.data) {
      console.error(`错误数据: ${error.data}`);
    }
  }
}

// 执行主函数
main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
