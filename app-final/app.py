from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_socketio import SocketIO
import json
import time
import threading
import logging
import sys
import os
from datetime import datetime

# 导入代理系统模块
from central_agent import CentralAgent
from agent_interceptor import interceptor
from main import initialize_agents, process_user_query

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 初始化Flask应用
app = Flask(__name__)
app.config['SECRET_KEY'] = 'multi-agent-visualization'

# 初始化SocketIO
socketio = SocketIO(app, cors_allowed_origins="*")

# 存储客户端连接
clients = []

# 保存最近的交互和响应
recent_interactions = []
recent_responses = {}

# 最大存储的交互数量
MAX_INTERACTIONS = 100

# 加载配置
def load_config():
    """从config.txt加载配置"""
    config = {}
    try:
        with open("config.txt", "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    try:
                        # 拆分行到等号，只取第一个等号
                        key_value = line.split("=", 1)
                        if len(key_value) == 2:
                            key, value = key_value
                            # 移除值中的注释部分
                            if "#" in value:
                                value = value.split("#")[0]
                            # 去除前后空格和引号
                            config[key.strip()] = value.strip().strip('"').strip("'")
                    except ValueError:
                        continue
    except Exception as e:
        logger.error(f"加载配置文件失败: {str(e)}")
    
    # 设置默认值
    if "ALARM_INTERVAL" not in config:
        config["ALARM_INTERVAL"] = "20000"  # 默认20秒
    if "ALARM_INITIAL_DELAY" not in config:
        config["ALARM_INITIAL_DELAY"] = "5000"  # 默认5秒
    
    logger.info(f"配置加载完成: {config}")
    return config

# 全局配置
CONFIG = load_config()

# 初始化代理系统
agents = initialize_agents()
user_agent = agents["user_agent"]
print("代理系统已初始化，准备接收Web请求")

# 存储交互历史
interaction_history = {
    "messages": [],
    "api_calls": []
}

# 确保目录存在
HISTORY_FILE = "history.txt"

# 加载已有历史（如果有）
if os.path.exists(HISTORY_FILE):
    try:
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                interaction = json.loads(line.strip())
                interaction_history["messages"].append(interaction)
    except Exception as e:
        print(f"加载历史记录错误: {e}")

@app.route('/')
def index():
    """渲染主页"""
    return render_template('index.html', history=interaction_history)

@app.route('/static/<path:path>')
def serve_static(path):
    """提供静态文件"""
    return send_from_directory('static', path)

@app.route('/api/config', methods=['GET'])
def get_config():
    """获取配置信息"""
    return jsonify({
        "alarm_interval": int(CONFIG.get("ALARM_INTERVAL", 20000)),
        "alarm_initial_delay": int(CONFIG.get("ALARM_INITIAL_DELAY", 5000))
    })

@app.route('/api/process', methods=['POST'])
def process_request():
    try:
        data = request.json
        user_message = data.get('message', '')
        
        # 模拟处理逻辑
        # 这里可以添加实际的处理逻辑，调用各种代理处理请求
        
        # 模拟回复
        response = {
            "formatted_response": f"您的请求 '{user_message}' 已处理。这是一个模拟回复。"
        }
        
        # 广播消息，通知前端有新的交互
        broadcast_interaction("System", "CentralAgent", "用户请求已接收", "message")
        
        # 模拟各代理之间的交互
        simulate_agent_interactions(user_message)
        
        return jsonify(response)
    except Exception as e:
        logger.error(f"处理请求出错: {str(e)}")
        return jsonify({"error": f"处理请求时出错: {str(e)}"}), 500

@app.route('/api/analyze_tx', methods=['POST'])
def analyze_tx():
    """分析区块链交易"""
    try:
        data = request.json

        if not data:
            return jsonify({'error': '未提供数据'}), 400

        tx_hash = data.get('tx_hash', '')

        if not tx_hash:
            return jsonify({'error': '未提供交易哈希'}), 400
            
        # 向客户端发送系统消息，表示正在分析交易
        socketio.emit('message', json.dumps({
            'type': 'system',
            'source': 'System',
            'target': 'User',
            'content': f'正在分析交易: {tx_hash}',
            'timestamp': time.time()
        }))

        # 处理交易分析
        result = process_user_query(user_agent, f"分析交易: {tx_hash}")

        # 添加到历史记录
        history_entry = {
            'timestamp': datetime.now().isoformat(),
            'user_message': f"分析交易: {tx_hash}",
            'response': result
        }

        interaction_history["messages"].append(history_entry)

        # 保存历史记录
        try:
            with open(HISTORY_FILE, 'a', encoding='utf-8') as f:
                f.write(json.dumps(history_entry, ensure_ascii=False) + '\n')
        except Exception as e:
            print(f"保存历史记录错误: {e}")
            
        # 发送完成消息
        socketio.emit('message', json.dumps({
            'type': 'system',
            'source': 'System',
            'target': 'User',
            'content': '交易分析完成',
            'timestamp': time.time()
        }))

        return jsonify(result)

    except Exception as e:
        print(f"分析交易错误: {e}")
        
        # 发送错误消息
        socketio.emit('message', json.dumps({
            'type': 'system',
            'source': 'System',
            'target': 'User',
            'content': f'分析交易时发生错误: {str(e)}',
            'timestamp': time.time()
        }))
        
        return jsonify({'error': str(e)}), 500

@app.route('/api/get_messages', methods=['GET'])
def get_messages():
    """获取拦截的消息用于可视化"""
    return jsonify(interaction_history)

@app.route('/api/save_history', methods=['POST'])
def save_history():
    try:
        data = request.json
        
        # 验证MCP协议消息格式
        if "protocol" in data and data["protocol"] == "MCP":
            # 已经是MCP协议格式，直接保存
            with open(HISTORY_FILE, 'a', encoding='utf-8') as f:
                f.write(json.dumps(data, ensure_ascii=False) + '\n')
            return jsonify({"success": True})
        else:
            # 旧格式，验证并转换
            if not all(key in data for key in ['sender', 'receiver', 'message', 'timestamp']):
                return jsonify({"error": "缺少必要字段"}), 400
            
            # 转换为MCP协议格式
            timestamp = time.time()
            message_id = f"{int(timestamp * 1000000)}-{hash(data['sender']+data['receiver']) % 10000}"
            
            mcp_message = {
                "version": "1.0",
                "protocol": "MCP",
                "message_id": message_id,
                "timestamp": timestamp,
                "source": {
                    "agent_id": data['sender'],
                    "agent_type": get_agent_type(data['sender'])
                },
                "target": {
                    "agent_id": data['receiver'],
                    "agent_type": get_agent_type(data['receiver'])
                },
                "type": "message",
                "content": data['message'],
                "metadata": {
                    "priority": "normal",
                    "processed": False
                }
            }
            
            # 保存转换后的消息
            with open(HISTORY_FILE, 'a', encoding='utf-8') as f:
                f.write(json.dumps(mcp_message, ensure_ascii=False) + '\n')
            
            return jsonify({"success": True})
    except Exception as e:
        logger.error(f"保存历史记录出错: {str(e)}")
        return jsonify({"error": f"保存历史记录出错: {str(e)}"}), 500

@app.route('/api/save_key', methods=['POST'])
def save_key():
    """保存提取的key到key.txt文件"""
    try:
        data = request.json
        extracted_key = data.get('key', '')
        
        if not extracted_key:
            return jsonify({"error": "未提供key数据"}), 400
        
        # 以追加模式写入key.txt
        with open("key.txt", 'a', encoding='utf-8') as f:
            f.write(f"{extracted_key}\n")
        
        return jsonify({"success": True, "message": f"成功保存key: {extracted_key}"})
    except Exception as e:
        logger.error(f"保存key出错: {str(e)}")
        return jsonify({"error": f"保存key出错: {str(e)}"}), 500

@app.route('/api/call_contract', methods=['POST'])
def call_contract():
    """调用合约API，使用key.txt中的数据"""
    try:
        # 读取key.txt最后一行
        last_line = ""
        try:
            with open("key.txt", 'r', encoding='utf-8') as f:
                lines = f.readlines()
                if lines:
                    last_line = lines[-1].strip()
                    logger.info(f"从key.txt读取的最后一行: {last_line}")
                else:
                    logger.warning("key.txt文件为空，将使用默认值")
        except Exception as e:
            logger.error(f"读取key.txt失败: {str(e)}")
            return jsonify({"error": f"读取key.txt失败: {str(e)}"}), 500
        
        # 解析最后一行数据
        parts = last_line.split(',')
        logger.info(f"解析后的数据: {parts}")
        
        # 提取数量，默认为100
        amount = 100
        try:
            # 尝试从第二个部分提取数字 (索引1)
            if len(parts) > 1:
                amount_str = parts[1].strip()
                amount = int(amount_str)
                logger.info(f"成功从key.txt提取数量: {amount}")
            else:
                logger.warning("无法从key.txt提取数量，使用默认值100")
        except (ValueError, IndexError) as e:
            logger.warning(f"转换数量时出错: {str(e)}，使用默认值100")
        
        # 固定的代币地址（使用实际地址）
        tka_address = "0x8Fd7e4A68deE8F92Ef92bEC58b369C3e926141Aa"
        tkb_address = "0x5BBae9C6741e31A1C0088334be84e6c09598c027"
        
        # 使用用户提供的合约地址
        contract_address = "0xF6FB382D0B6086093bEe37d01230fa51D2b9a567"
        
        # 智能合约ABI (部分)
        contract_abi = [
            {
                "inputs": [
                    {"internalType": "address", "name": "tokenA", "type": "address"},
                    {"internalType": "address", "name": "tokenB", "type": "address"},
                    {"internalType": "uint256", "name": "amountA", "type": "uint256"}
                ],
                "name": "swapTokens",
                "outputs": [],
                "stateMutability": "nonpayable",
                "type": "function"
            }
        ]
        
        # 模拟合约调用
        broadcast_interaction("User", "WalletAgent", f"请求调用合约交换代币")
        time.sleep(0.3)
        broadcast_interaction("WalletAgent", "API", f"调用合约: {contract_address} 交换 {amount} 个 TKA 到 TKB", "api_call")
        time.sleep(0.5)
        
        # 构建合约调用结果
        result = {
            "success": True,
            "contract_call": {
                "contract_address": contract_address,
                "contract_abi": contract_abi,
                "from_token": {
                    "symbol": "TKA",
                    "address": tka_address,
                    "decimals": 18
                },
                "to_token": {
                    "symbol": "TKB",
                    "address": tkb_address,
                    "decimals": 18
                },
                "amount": amount,
                "timestamp": time.time(),
                "status": "pending",
                "method": "swap",
                "chain_id": 97,  # BSC测试网 (Binance Smart Chain Testnet)
                "tx_hash": f"0x{hash(f'{contract_address}{tka_address}{tkb_address}{amount}{time.time()}') % (10**64):064x}"
            }
        }
        
        # 模拟交易完成
        broadcast_interaction("API", "WalletAgent", f"已准备合约 {contract_address} 调用数据，等待钱包签名", "api_response")
        
        return jsonify(result)
    except Exception as e:
        logger.error(f"调用合约出错: {str(e)}")
        return jsonify({"error": f"调用合约出错: {str(e)}"}), 500

@socketio.on('connect')
def handle_connect():
    """处理客户端连接"""
    client_id = request.sid
    clients.append(client_id)
    interceptor.add_client(client_id)
    logger.info(f"客户端 {client_id} 已连接")

    # 发送欢迎消息
    socketio.emit('message', json.dumps({
        'type': 'system',
        'source': 'System',
        'target': 'Client',
        'content': '已连接到区块链多代理可视化系统',
        'timestamp': time.time()
    }), room=client_id)
    
    # 不再发送初始动画，由前端的Alarm Agent定时任务控制
    # send_initial_animations()

@socketio.on('disconnect')
def handle_disconnect():
    """处理客户端断开连接"""
    client_id = request.sid
    if client_id in clients:
        clients.remove(client_id)
        interceptor.remove_client(client_id)
        logger.info(f"客户端 {client_id} 已断开连接")

# 注释掉不需要的send_initial_animations函数，避免干扰
"""
def send_initial_animations():
    # 这个函数不再使用，由前端的Alarm Agent定时任务控制
    pass
"""

# 设置拦截器广播函数
def broadcast_interaction(source, target, content, interaction_type="message"):
    """广播交互信息到所有客户端"""
    timestamp = time.time()
    message_id = f"{int(timestamp * 1000000)}-{hash(source+target+content) % 10000}"
    
    # 构建MCP协议格式的消息
    mcp_message = {
        "version": "1.0",
        "protocol": "MCP",
        "message_id": message_id,
        "timestamp": timestamp,
        "source": {
            "agent_id": source,
            "agent_type": get_agent_type(source)
        },
        "target": {
            "agent_id": target,
            "agent_type": get_agent_type(target)
        },
        "type": interaction_type,
        "content": content,
        "metadata": {
            "priority": "normal",
            "processed": False
        }
    }
    
    # 简化版本用于客户端显示
    interaction = {
        "source": source,
        "target": target,
        "content": content,
        "type": interaction_type,
        "timestamp": timestamp
    }
    
    # 保存到历史记录
    if interaction_type == "message":
        interaction_history["messages"].append(interaction)
    else:
        interaction_history["api_calls"].append(interaction)
    
    # 限制历史记录大小
    max_history = 100
    if len(interaction_history["messages"]) > max_history:
        interaction_history["messages"] = interaction_history["messages"][-max_history:]
    if len(interaction_history["api_calls"]) > max_history:
        interaction_history["api_calls"] = interaction_history["api_calls"][-max_history:]
    
    # 保存到history.txt (JSONL格式) - 使用MCP消息格式
    with open(HISTORY_FILE, 'a', encoding='utf-8') as f:
        f.write(json.dumps(mcp_message, ensure_ascii=False) + '\n')
    
    # 通过WebSocket发送到客户端
    socketio.emit('message', interaction)

def get_agent_type(agent_id):
    """获取代理类型"""
    agent_types = {
        "CentralAgent": "central",
        "InfoProcessAgent": "processor",
        "MultiAgents": "dispatcher",
        "DataCleanAgent": "data_cleaner",
        "CEXWithdrawAgent": "specialist",
        "WhaleAgent": "specialist",
        "TxAgent": "specialist",
        "ContractMonitorAgent": "specialist",
        "BasicInfoAgent": "specialist",
        "AlarmAgent": "notification",
        "WalletAgent": "executor",
        "CEXAgent": "executor",
        "AutoTradeAgent": "executor",
        "API": "external_service",
        "LLMAPI": "external_service",
        "BlockchainAPI": "external_service",
        "System": "system",
        "User": "user",
        "Client": "user",
        "ApprovalTx": "action",
        "PlaceOrder": "action",
        "MessageCall": "action"
    }
    return agent_types.get(agent_id, "unknown")

def simulate_agent_interactions(user_message):
    """模拟代理之间的交互"""
    # 模拟中央代理分发任务
    broadcast_interaction("CentralAgent", "InfoProcessAgent", f"获取相关信息: {user_message}")
    time.sleep(0.5)
    
    # 模拟信息处理代理向专业代理分发任务
    broadcast_interaction("InfoProcessAgent", "MultiAgents", "分配数据获取任务")
    time.sleep(0.3)
    
    # 模拟专业代理执行任务
    agents = ["CEXWithdrawAgent", "WhaleAgent", "TxAgent", "ContractMonitorAgent", "BasicInfoAgent"]
    for agent in agents:
        broadcast_interaction("MultiAgents", agent, f"执行数据收集: {user_message[:20]}...")
        time.sleep(0.2)
    
    # 模拟API调用
    broadcast_interaction("BasicInfoAgent", "API", "获取币价信息", "api_call")
    time.sleep(0.5)
    broadcast_interaction("API", "BasicInfoAgent", "返回币价数据", "api_response")
    
    # 模拟数据清理
    broadcast_interaction("MultiAgents", "DataCleanAgent", "数据整合与清理")
    time.sleep(0.4)
    
    # 模拟向中央代理返回结果
    broadcast_interaction("DataCleanAgent", "CentralAgent", "数据处理完成")
    
    # 模拟警报触发
    if "警报" in user_message or "紧急" in user_message:
        broadcast_interaction("CentralAgent", "AlarmAgent", "触发警报系统")
        time.sleep(0.3)
        broadcast_interaction("AlarmAgent", "MessageCall", "发送紧急通知")
    
    # 模拟交易操作
    if "交易" in user_message or "买入" in user_message or "卖出" in user_message:
        broadcast_interaction("CentralAgent", "AutoTradeAgent", "准备执行交易")
        time.sleep(0.3)
        broadcast_interaction("AutoTradeAgent", "WalletAgent", "请求交易授权")
        time.sleep(0.4)
        broadcast_interaction("WalletAgent", "ApprovalTx", "确认交易授权")
        time.sleep(0.3)
        broadcast_interaction("AutoTradeAgent", "CEXAgent", "提交交易订单")
        time.sleep(0.3)
        broadcast_interaction("CEXAgent", "PlaceOrder", "订单已提交")

if __name__ == '__main__':
    # 清空 history.txt 文件
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        pass
    print(f"🧹 已清空 {HISTORY_FILE} 文件")
    
    # 清空 llm.txt 文件
    with open("llm.txt", 'w', encoding='utf-8') as f:
        pass
    print(f"🧹 已清空 llm.txt 文件")
    
    # 测试写入llm.txt，确保权限和路径正确
    try:
        with open("llm.txt", 'a', encoding='utf-8') as f:
            f.write(json.dumps({
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "test": "这是一个启动时的测试写入",
                "path": os.path.abspath("llm.txt")
            }, ensure_ascii=False) + "\n")
        print(f"✅ 测试写入llm.txt成功，文件路径: {os.path.abspath('llm.txt')}")
    except Exception as e:
        print(f"❌ 测试写入llm.txt失败: {str(e)}")
    
    socketio.run(app, host='0.0.0.0', port=8080, debug=True)