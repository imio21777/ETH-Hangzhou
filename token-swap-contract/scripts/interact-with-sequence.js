// 与SequenceStorage合约交互的脚本
const hre = require("hardhat");
const { ethers } = require("hardhat");

async function main() {
  // 获取部署网络信息
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

  // 开始菜单
  await showMenu(sequenceStorage, signer);
}

async function showMenu(sequenceStorage, signer) {
  console.log("\n==== SequenceStorage合约交互菜单 ====");
  console.log("1. 存储新序列");
  console.log("2. 获取序列信息");
  console.log("3. 验证序列");
  console.log("4. 验证序列并记录事件");
  console.log("5. 获取用户的所有序列");
  console.log("6. 退出");

  // 在命令行中接收用户输入
  const readline = require("readline").createInterface({
    input: process.stdin,
    output: process.stdout,
  });

  readline.question("请选择操作 (1-6): ", async (choice) => {
    readline.close();

    switch (choice) {
      case "1":
        await storeNewSequence(sequenceStorage, signer);
        break;
      case "2":
        await getSequenceInfo(sequenceStorage, signer);
        break;
      case "3":
        await verifySequence(sequenceStorage, signer);
        break;
      case "4":
        await recordVerification(sequenceStorage, signer);
        break;
      case "5":
        await getUserSequences(sequenceStorage, signer);
        break;
      case "6":
        console.log("退出程序");
        process.exit(0);
      default:
        console.log("无效选择，请重新选择");
        await showMenu(sequenceStorage, signer);
    }
  });
}

// 1. 存储新序列
async function storeNewSequence(sequenceStorage, signer) {
  const readline = require("readline").createInterface({
    input: process.stdin,
    output: process.stdout,
  });

  readline.question(
    "输入序列值，用逗号分隔 (例如: 1,2,3,4,5): ",
    async (input) => {
      readline.close();

      try {
        // 解析输入为数字数组
        const values = input.split(",").map((val) => parseInt(val.trim()));
        console.log(`准备存储序列: [${values}]`);

        // 调用合约存储序列
        const tx = await sequenceStorage.storeSequence(values);
        console.log(`交易已提交，等待确认...`);

        const receipt = await tx.wait();

        // 从事件中获取序列ID
        const event = receipt.logs[0];
        const iface = sequenceStorage.interface;
        const decodedEvent = iface.parseLog(event);

        if (decodedEvent && decodedEvent.name === "SequenceStored") {
          console.log(`序列存储成功!`);
          console.log(`序列ID: ${decodedEvent.args.sequenceId}`);
          console.log(`存储的序列值: [${decodedEvent.args.values}]`);
        } else {
          console.log(`无法解析事件，但交易已确认。交易哈希: ${receipt.hash}`);
        }
      } catch (error) {
        console.error(`错误: ${error.message}`);
      }

      // 返回主菜单
      await showMenu(sequenceStorage, signer);
    }
  );
}

// 2. 获取序列信息
async function getSequenceInfo(sequenceStorage, signer) {
  const readline = require("readline").createInterface({
    input: process.stdin,
    output: process.stdout,
  });

  readline.question("输入序列ID: ", async (sequenceId) => {
    readline.close();

    try {
      console.log(`获取序列信息，ID: ${sequenceId}`);

      // 调用合约获取序列
      const [values, timestamp] = await sequenceStorage.getSequence(sequenceId);

      console.log(`序列值: [${values}]`);
      console.log(`存储时间戳: ${timestamp}`);
      console.log(`存储日期: ${new Date(timestamp * 1000).toLocaleString()}`);
    } catch (error) {
      console.error(`错误: ${error.message}`);
    }

    // 返回主菜单
    await showMenu(sequenceStorage, signer);
  });
}

// 3. 验证序列
async function verifySequence(sequenceStorage, signer) {
  const readline = require("readline").createInterface({
    input: process.stdin,
    output: process.stdout,
  });

  readline.question("输入序列ID: ", async (sequenceId) => {
    readline.question(
      "输入要验证的序列值，用逗号分隔 (例如: 1,2,3,4,5): ",
      async (input) => {
        readline.close();

        try {
          // 解析输入为数字数组
          const values = input.split(",").map((val) => parseInt(val.trim()));
          console.log(`验证序列: [${values}]`);

          // 调用合约验证序列
          const mismatchIndex = await sequenceStorage.verifySequence(
            sequenceId,
            values
          );

          if (mismatchIndex.toString() === ethers.MaxUint256.toString()) {
            console.log(`验证成功! 序列完全匹配`);
          } else {
            console.log(`验证失败! 第一个不匹配的元素在索引 ${mismatchIndex}`);
          }
        } catch (error) {
          console.error(`错误: ${error.message}`);
        }

        // 返回主菜单
        await showMenu(sequenceStorage, signer);
      }
    );
  });
}

// 4. 验证序列并记录事件
async function recordVerification(sequenceStorage, signer) {
  const readline = require("readline").createInterface({
    input: process.stdin,
    output: process.stdout,
  });

  readline.question("输入序列ID: ", async (sequenceId) => {
    readline.question(
      "输入要验证的序列值，用逗号分隔 (例如: 1,2,3,4,5): ",
      async (input) => {
        readline.close();

        try {
          // 解析输入为数字数组
          const values = input.split(",").map((val) => parseInt(val.trim()));
          console.log(`验证序列并记录事件: [${values}]`);

          // 调用合约验证序列并记录事件
          const tx = await sequenceStorage.recordVerification(
            sequenceId,
            values
          );
          console.log(`交易已提交，等待确认...`);

          const receipt = await tx.wait();

          // 解析事件
          const event = receipt.logs[0];
          const iface = sequenceStorage.interface;
          const decodedEvent = iface.parseLog(event);

          if (decodedEvent && decodedEvent.name === "SequenceVerified") {
            console.log(`验证事件已记录!`);
            console.log(
              `验证结果: ${decodedEvent.args.success ? "成功" : "失败"}`
            );
            if (!decodedEvent.args.success) {
              console.log(`不匹配索引: ${decodedEvent.args.mismatchIndex}`);
            }
          } else {
            console.log(
              `无法解析事件，但交易已确认。交易哈希: ${receipt.hash}`
            );
          }
        } catch (error) {
          console.error(`错误: ${error.message}`);
        }

        // 返回主菜单
        await showMenu(sequenceStorage, signer);
      }
    );
  });
}

// 5. 获取用户的所有序列
async function getUserSequences(sequenceStorage, signer) {
  const readline = require("readline").createInterface({
    input: process.stdin,
    output: process.stdout,
  });

  readline.question("输入用户地址 (留空使用当前账户): ", async (address) => {
    readline.close();

    try {
      // 如果未提供地址，使用当前签名者地址
      const userAddress = address.trim() || signer.address;
      console.log(`获取用户 ${userAddress} 的所有序列`);

      // 调用合约获取用户序列
      const sequenceIds = await sequenceStorage.getUserSequences(userAddress);

      if (sequenceIds.length === 0) {
        console.log(`该用户没有存储的序列`);
      } else {
        console.log(`找到 ${sequenceIds.length} 个序列:`);
        for (let i = 0; i < sequenceIds.length; i++) {
          console.log(`${i + 1}. ${sequenceIds[i]}`);

          // 可选：获取每个序列的详细信息
          try {
            const [values, timestamp] = await sequenceStorage.getSequence(
              sequenceIds[i]
            );
            console.log(`   值: [${values}]`);
            console.log(
              `   时间: ${new Date(timestamp * 1000).toLocaleString()}`
            );
          } catch (e) {
            console.log(`   无法获取详情: ${e.message}`);
          }
        }
      }
    } catch (error) {
      console.error(`错误: ${error.message}`);
    }

    // 返回主菜单
    await showMenu(sequenceStorage, signer);
  });
}

// 执行主函数
main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
