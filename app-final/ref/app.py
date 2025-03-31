from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_socketio import SocketIO
import json
import time
import threading
import logging
import sys
import os
from datetime import datetime

# 添加当前目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

# 导入代理系统模块
from central_agent import CentralAgent
from agent_interceptor import interceptor
from main import initialize_agents, process_user_request
# 导入翻译模块
from translate import translate_response

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

# Initialize the agent system once
central_agent = initialize_agents()
print("Agent system initialized for web app")

# Store interaction history
interaction_history = []
history_file = 'interaction_history.json'

# Load existing history if available
if os.path.exists(history_file):
    try:
        with open(history_file, 'r', encoding='utf-8') as f:
            interaction_history = json.load(f)
    except Exception as e:
        print(f"Error loading history: {e}")

@app.route('/')
def index():
    """渲染主页"""
    return render_template('index.html', history=interaction_history)

@app.route('/static/<path:path>')
def serve_static(path):
    """提供静态文件"""
    return send_from_directory('static', path)

@app.route('/api/process', methods=['POST'])
def process():
    """处理用户请求并返回结果"""
    try:
        data = request.json

        if not data:
            return jsonify({'error': 'No data provided'}), 400

        user_message = data.get('message', '')

        if not user_message:
            return jsonify({'error': 'No message provided'}), 400

        # Process the request
        result = process_user_request(central_agent, user_message)

        # Add to history
        history_entry = {
            'timestamp': datetime.now().isoformat(),
            'user_message': user_message,
            'response': result
        }

        interaction_history.append(history_entry)

        # Save history (in a real app, this would be done more efficiently)
        try:
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(interaction_history, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving history: {e}")

        return jsonify(result)

    except Exception as e:
        print(f"Error processing request: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/analyze_tx', methods=['POST'])
def analyze_tx():
    """分析区块链交易"""
    try:
        data = request.json

        if not data:
            return jsonify({'error': 'No data provided'}), 400

        tx_hash = data.get('tx_hash', '')

        if not tx_hash:
            return jsonify({'error': 'No transaction hash provided'}), 400

        # Process the transaction analysis
        result = process_user_request(central_agent, {"tx_hash": tx_hash})

        # Add to history
        history_entry = {
            'timestamp': datetime.now().isoformat(),
            'user_message': f"Analyze transaction: {tx_hash}",
            'response': result
        }

        interaction_history.append(history_entry)

        # Save history
        try:
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(interaction_history, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving history: {e}")

        return jsonify(result)

    except Exception as e:
        print(f"Error analyzing transaction: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/get_messages')
def get_messages():
    """Get intercepted messages for visualization"""
    return jsonify({
        'messages': interceptor.get_messages(),
        'api_calls': interceptor.get_api_calls()
    })

@app.route('/api/clear_history', methods=['POST'])
def clear_history():
    """Clear interaction history"""
    global interaction_history
    interaction_history = []

    # Save empty history
    try:
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump(interaction_history, f, indent=2)
    except Exception as e:
        print(f"Error saving history: {e}")

    return jsonify({'success': True})

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

@socketio.on('disconnect')
def handle_disconnect():
    """处理客户端断开连接"""
    client_id = request.sid
    if client_id in clients:
        clients.remove(client_id)
        interceptor.remove_client(client_id)
        logger.info(f"客户端 {client_id} 已断开连接")

# 设置拦截器广播函数
def broadcast_message(message):
    """广播消息给所有客户端"""
    # 保存消息到历史记录
    try:
        message_obj = message if isinstance(message, dict) else json.loads(message)
        recent_interactions.append(message_obj)

        # 限制历史记录大小
        while len(recent_interactions) > MAX_INTERACTIONS:
            recent_interactions.pop(0)
    except:
        pass

    # 广播消息
    socketio.emit('message', message)

# 设置拦截器的广播函数
interceptor._broadcast_func = broadcast_message

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=8080, debug=True)
