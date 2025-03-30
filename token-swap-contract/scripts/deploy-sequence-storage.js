// 部署和测试SequenceStorage合约的脚本
const hre = require("hardhat");

async function main() {
  console.log("开始部署SequenceStorage合约...");

  // 部署合约
  const SequenceStorage = await hre.ethers.getContractFactory(
    "SequenceStorage"
  );
  const sequenceStorage = await SequenceStorage.deploy();

  await sequenceStorage.waitForDeployment();

  const sequenceStorageAddress = await sequenceStorage.getAddress();
  console.log(`SequenceStorage合约已部署到: ${sequenceStorageAddress}`);

  // 测试存储序列
  console.log("\n测试存储序列...");
  const testSequence = [1, 2, 3, 4, 5];
  const storeTx = await sequenceStorage.storeSequence(testSequence);
  const storeReceipt = await storeTx.wait();

  // 从事件中获取序列ID
  const storeEvent = storeReceipt.logs[0];
  const iface = sequenceStorage.interface;
  const decodedEvent = iface.parseLog(storeEvent);
  const sequenceId = decodedEvent.args.sequenceId;

  console.log(`序列已存储，序列ID: ${sequenceId}`);

  // 获取序列
  console.log("\n获取存储的序列...");
  const [values, timestamp] = await sequenceStorage.getSequence(sequenceId);
  console.log(`序列值: [${values}]`);
  console.log(`存储时间戳: ${timestamp}`);

  // 验证正确的序列
  console.log("\n验证正确的序列...");
  const verifyTx = await sequenceStorage.verifySequence(
    sequenceId,
    testSequence
  );
  const verifyReceipt = await verifyTx.wait();
  const verifyEvent = verifyReceipt.logs[0];
  const decodedVerifyEvent = iface.parseLog(verifyEvent);
  console.log(
    `序列验证结果: ${decodedVerifyEvent.args.success ? "成功" : "失败"}`
  );
  console.log(`不匹配索引: ${decodedVerifyEvent.args.mismatchIndex}`);

  // 验证错误的序列 (中间值不同)
  console.log("\n验证中间值不同的序列...");
  const wrongMiddleSequence = [...testSequence];
  wrongMiddleSequence[2] = 999; // 修改第三个元素
  const wrongMiddleTx = await sequenceStorage.verifySequence(
    sequenceId,
    wrongMiddleSequence
  );
  const wrongMiddleReceipt = await wrongMiddleTx.wait();
  const wrongMiddleEvent = wrongMiddleReceipt.logs[0];
  const decodedWrongMiddleEvent = iface.parseLog(wrongMiddleEvent);
  console.log(
    `序列验证结果: ${decodedWrongMiddleEvent.args.success ? "成功" : "失败"}`
  );
  console.log(`不匹配索引: ${decodedWrongMiddleEvent.args.mismatchIndex}`);

  // 验证错误的序列 (长度不同)
  console.log("\n验证长度不同的序列...");
  const shortSequence = testSequence.slice(0, 3); // 只取前3个
  const shortTx = await sequenceStorage.verifySequence(
    sequenceId,
    shortSequence
  );
  const shortReceipt = await shortTx.wait();
  const shortEvent = shortReceipt.logs[0];
  const decodedShortEvent = iface.parseLog(shortEvent);
  console.log(
    `序列验证结果: ${decodedShortEvent.args.success ? "成功" : "失败"}`
  );
  console.log(`不匹配索引: ${decodedShortEvent.args.mismatchIndex}`);

  // 查询用户的所有序列
  console.log("\n获取用户的所有序列...");
  const [deployer] = await ethers.getSigners();
  const userSequences = await sequenceStorage.getUserSequences(
    deployer.address
  );
  console.log(`用户序列IDs: ${userSequences}`);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
