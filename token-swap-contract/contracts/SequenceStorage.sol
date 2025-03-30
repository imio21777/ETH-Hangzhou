// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title SequenceStorage
 * @dev 用于存储和验证序列值的合约
 */
contract SequenceStorage is Ownable {
    // 序列存储结构
    struct Sequence {
        uint256[] values;
        uint256 timestamp;
        bool exists;
    }

    // 序列ID到序列数据的映射
    mapping(bytes32 => Sequence) private sequences;

    // 用户地址到他们的序列ID列表的映射
    mapping(address => bytes32[]) private userSequences;

    // 事件
    event SequenceStored(
        address indexed user,
        bytes32 indexed sequenceId,
        uint256[] values
    );
    event SequenceVerified(
        address indexed verifier,
        bytes32 indexed sequenceId,
        bool success,
        uint256 mismatchIndex
    );

    constructor() Ownable(msg.sender) {}

    /**
     * @dev 存储一个新的序列
     * @param values 要存储的序列值数组
     * @return sequenceId 存储的序列ID
     */
    function storeSequence(
        uint256[] calldata values
    ) external returns (bytes32) {
        require(values.length > 0, "Sequence cannot be empty");

        // 生成序列ID (用户地址 + 时间戳的哈希)
        bytes32 sequenceId = keccak256(
            abi.encodePacked(msg.sender, block.timestamp, values)
        );

        // 确保ID不重复
        require(!sequences[sequenceId].exists, "Sequence ID already exists");

        // 存储序列数据
        sequences[sequenceId] = Sequence({
            values: values,
            timestamp: block.timestamp,
            exists: true
        });

        // 将序列ID添加到用户的序列列表中
        userSequences[msg.sender].push(sequenceId);

        // 触发事件
        emit SequenceStored(msg.sender, sequenceId, values);

        return sequenceId;
    }

    /**
     * @dev 获取序列数据
     * @param sequenceId 序列ID
     * @return values 序列值
     * @return timestamp 存储时间戳
     */
    function getSequence(
        bytes32 sequenceId
    ) external view returns (uint256[] memory values, uint256 timestamp) {
        require(sequences[sequenceId].exists, "Sequence does not exist");
        Sequence storage seq = sequences[sequenceId];
        return (seq.values, seq.timestamp);
    }

    /**
     * @dev 验证序列是否匹配
     * @param sequenceId 序列ID
     * @param values 要验证的序列值
     * @return mismatchIndex 如果验证成功返回type(uint256).max，否则返回第一个不匹配元素的索引
     */
    function verifySequence(
        bytes32 sequenceId,
        uint256[] calldata values
    ) external view returns (uint256 mismatchIndex) {
        require(sequences[sequenceId].exists, "Sequence does not exist");

        Sequence storage storedSeq = sequences[sequenceId];

        // 初始化为最大值，表示没有不匹配的元素
        mismatchIndex = type(uint256).max;

        // 检查长度是否相同
        if (storedSeq.values.length != values.length) {
            // 返回较短数组的长度作为不匹配索引
            mismatchIndex = storedSeq.values.length < values.length
                ? storedSeq.values.length
                : values.length;
        } else {
            // 逐个比较值
            for (uint i = 0; i < values.length; i++) {
                if (storedSeq.values[i] != values[i]) {
                    mismatchIndex = i;
                    break;
                }
            }
        }

        return mismatchIndex;
    }

    /**
     * @dev 获取用户的所有序列ID
     * @param user 用户地址
     * @return 用户的序列ID数组
     */
    function getUserSequences(
        address user
    ) external view returns (bytes32[] memory) {
        return userSequences[user];
    }

    /**
     * @dev 检查序列是否存在
     * @param sequenceId 序列ID
     * @return 如果序列存在返回true，否则返回false
     */
    function sequenceExists(bytes32 sequenceId) external view returns (bool) {
        return sequences[sequenceId].exists;
    }

    // 单独添加一个记录验证事件的函数
    function recordVerification(
        bytes32 sequenceId,
        uint256[] calldata values
    ) external returns (uint256) {
        uint256 mismatchIndex = this.verifySequence(sequenceId, values);
        bool success = mismatchIndex == type(uint256).max;
        emit SequenceVerified(msg.sender, sequenceId, success, mismatchIndex);
        return mismatchIndex;
    }
}
