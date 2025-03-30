const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("SequenceStorage", function () {
  let sequenceStorage;
  let owner;
  let addr1;
  let testSequence;
  let sequenceId;

  beforeEach(async function () {
    // 获取合约和签名者
    [owner, addr1] = await ethers.getSigners();

    // 部署合约
    const SequenceStorage = await ethers.getContractFactory("SequenceStorage");
    sequenceStorage = await SequenceStorage.deploy();
    await sequenceStorage.waitForDeployment();

    // 测试用序列
    testSequence = [100, 200, 300, 400, 500];
  });

  describe("序列存储", function () {
    it("应该正确存储序列", async function () {
      // 存储序列
      const tx = await sequenceStorage.storeSequence(testSequence);
      const receipt = await tx.wait();

      // 获取事件信息
      const event = receipt.logs[0];
      const iface = sequenceStorage.interface;
      const decodedEvent = iface.parseLog(event);

      // 保存序列ID用于后续测试
      sequenceId = decodedEvent.args.sequenceId;

      // 验证事件参数
      expect(decodedEvent.name).to.equal("SequenceStored");
      expect(decodedEvent.args.user).to.equal(owner.address);

      // 获取序列数据并验证
      const [values, timestamp] = await sequenceStorage.getSequence(sequenceId);

      // 验证序列值
      expect(values.length).to.equal(testSequence.length);
      for (let i = 0; i < values.length; i++) {
        expect(values[i]).to.equal(testSequence[i]);
      }

      // 验证时间戳(应该是最近的)
      const blockTimestamp = (await ethers.provider.getBlock("latest"))
        .timestamp;
      expect(timestamp).to.be.lte(blockTimestamp);
    });

    it("不能存储空序列", async function () {
      await expect(sequenceStorage.storeSequence([])).to.be.revertedWith(
        "Sequence cannot be empty"
      );
    });
  });

  describe("序列验证", function () {
    beforeEach(async function () {
      // 存储测试序列
      const tx = await sequenceStorage.storeSequence(testSequence);
      const receipt = await tx.wait();
      const event = receipt.logs[0];
      const decodedEvent = sequenceStorage.interface.parseLog(event);
      sequenceId = decodedEvent.args.sequenceId;
    });

    it("应该验证正确的序列并返回最大uint256值", async function () {
      const result = await sequenceStorage.verifySequence(
        sequenceId,
        testSequence
      );
      // 检查返回值是最大的uint256
      expect(result).to.equal(ethers.MaxUint256);
    });

    it("应该在数组长度不同时返回较短数组的长度", async function () {
      // 较短的输入序列
      const shortSequence = testSequence.slice(0, 3); // 只取前3个
      const result = await sequenceStorage.verifySequence(
        sequenceId,
        shortSequence
      );
      expect(result).to.equal(3);

      // 检查事件 - 使用recordVerification函数
      const tx = await sequenceStorage.recordVerification(
        sequenceId,
        shortSequence
      );
      const receipt = await tx.wait();
      const event = receipt.logs[0];
      const decodedEvent = sequenceStorage.interface.parseLog(event);
      expect(decodedEvent.name).to.equal("SequenceVerified");
      expect(decodedEvent.args.success).to.be.false;
      expect(decodedEvent.args.mismatchIndex).to.equal(3);

      // 较长的输入序列
      const longSequence = [...testSequence, 600, 700];
      const longResult = await sequenceStorage.verifySequence(
        sequenceId,
        longSequence
      );
      expect(longResult).to.equal(5);
    });

    it("应该返回第一个不匹配元素的索引", async function () {
      // 修改第一个元素
      const wrongFirstSequence = [...testSequence];
      wrongFirstSequence[0] = 999;
      const firstResult = await sequenceStorage.verifySequence(
        sequenceId,
        wrongFirstSequence
      );
      expect(firstResult).to.equal(0);

      // 修改中间元素
      const wrongMiddleSequence = [...testSequence];
      wrongMiddleSequence[2] = 999;
      const middleResult = await sequenceStorage.verifySequence(
        sequenceId,
        wrongMiddleSequence
      );
      expect(middleResult).to.equal(2);

      // 修改最后一个元素
      const wrongLastSequence = [...testSequence];
      wrongLastSequence[4] = 999;
      const lastResult = await sequenceStorage.verifySequence(
        sequenceId,
        wrongLastSequence
      );
      expect(lastResult).to.equal(4);
    });

    it("应该拒绝不存在的序列ID", async function () {
      const fakeId = ethers.keccak256(ethers.toUtf8Bytes("不存在的ID"));
      await expect(
        sequenceStorage.verifySequence(fakeId, testSequence)
      ).to.be.revertedWith("Sequence does not exist");
    });
  });

  describe("用户查询", function () {
    it("应该返回用户的所有序列ID", async function () {
      // 存储3个序列
      const ids = [];
      for (let i = 0; i < 3; i++) {
        const seq = [i * 100, i * 200, i * 300];
        const tx = await sequenceStorage.storeSequence(seq);
        const receipt = await tx.wait();
        const event = receipt.logs[0];
        const decodedEvent = sequenceStorage.interface.parseLog(event);
        ids.push(decodedEvent.args.sequenceId);
      }

      // 获取用户的序列ID
      const userSequences = await sequenceStorage.getUserSequences(
        owner.address
      );

      // 验证数量和值
      expect(userSequences.length).to.equal(3);
      for (let i = 0; i < ids.length; i++) {
        expect(userSequences).to.include(ids[i]);
      }
    });

    it("应该返回空数组给没有序列的用户", async function () {
      const userSequences = await sequenceStorage.getUserSequences(
        addr1.address
      );
      expect(userSequences.length).to.equal(0);
    });
  });

  describe("权限控制", function () {
    it("只有所有者可以访问特定功能", async function () {
      // 测试可能的所有者特权功能
      // 在这个合约中，没有明确的特权功能，但未来可能会添加
    });
  });
});
