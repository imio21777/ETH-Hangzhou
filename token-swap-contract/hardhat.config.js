require("@nomicfoundation/hardhat-toolbox");
require("dotenv").config();

// 从.env文件或环境变量中获取私钥
const PRIVATE_KEY = process.env.PRIVATE_KEY || "";

/** @type import('hardhat/config').HardhatUserConfig */
module.exports = {
  solidity: "0.8.20",
  networks: {
    hardhat: {
      // forking: {
      //   // 如果你想模拟BSC网络（PancakeSwap所在的网络）
      //   url: "https://bsc-dataseed2.defibit.io/",

      //   // 你也可以选择模拟其他网络，例如以太坊主网
      //   // url: "https://eth-mainnet.alchemyapi.io/v2/YOUR-API-KEY",
      // },
      chainId: 31337,
      mining: {
        auto: true,
        interval: 0,
      },
    },
    // 添加其他网络配置，例如测试网或主网
    bscTestnet: {
      url: "https://data-seed-prebsc-1-s3.binance.org:8545",
      chainId: 97,
      accounts: PRIVATE_KEY ? [PRIVATE_KEY] : [],
      timeout: 60000,
    },

    bsc: {
      url: "https://bsc-dataseed.binance.org/",
      chainId: 56,
      accounts: process.env.PRIVATE_KEY ? [process.env.PRIVATE_KEY] : [],
    },
  },
  etherscan: {
    // BSC测试网的API密钥
    apiKey: {
      bscTestnet: process.env.BSC_API_KEY || "",
      bsc: process.env.BSC_API_KEY || "",
    },
  },
};
