import json
import time
import os
from typing import List, Dict, Any, Callable, Optional

class AgentInterceptor:
    """
    代理拦截器类，用于捕获和广播代理之间的交互
    """

    def __init__(self):
        """初始化拦截器"""
        self.clients = []  # 存储客户端连接ID
        self._broadcast_func = None  # 广播函数
        self.messages = []  # 存储消息历史
        self.api_calls = []  # 存储API调用历史
        self.max_history = 100  # 最大历史记录数
        # 加载延时配置
        self.delay_time = self._load_delay_config()

    def _load_delay_config(self) -> float:
        """加载延时配置"""
        delay_time = 0.0
        config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.txt')

        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as file:
                    for line in file:
                        line = line.strip()
                        # 跳过注释和空行
                        if not line or line.startswith('#'):
                            continue

                        # 解析键值对
                        if '=' in line and 'DELAY_TIME' in line:
                            key, value = line.split('=', 1)
                            if key.strip() == 'DELAY_TIME':
                                delay_time = float(value.strip().strip('"\''))
                                print(f"加载延时配置: {delay_time}秒")
                                break
            except Exception as e:
                print(f"加载延时配置错误: {e}")
                
        return delay_time

    def add_client(self, client):
        """
        添加客户端连接

        参数:
        client: 客户端标识符
        """
        if client not in self.clients:
            self.clients.append(client)

    def remove_client(self, client):
        """
        移除客户端连接

        参数:
        client: 客户端标识符
        """
        if client in self.clients:
            self.clients.remove(client)

    def intercept_message(self, source_agent: str, target_agent: str, message: str, message_type: str = "message"):
        """
        拦截代理之间的消息

        参数:
        source_agent: 源代理名称
        target_agent: 目标代理名称
        message: 消息内容
        message_type: 消息类型
        """
        message_data = {
            "type": message_type,
            "source": source_agent,
            "target": target_agent,
            "content": self._format_content(message),
            "timestamp": time.time()
        }

        # 保存消息历史
        self.messages.append(message_data)
        if len(self.messages) > self.max_history:
            self.messages.pop(0)

        self._broadcast(message_data)
        
        # 添加延时
        if self.delay_time > 0:
            time.sleep(self.delay_time)

    def intercept_api_call(self, agent_name: str, api_type: str, endpoint: str, params: Dict[str, Any]):
        """
        拦截API调用

        参数:
        agent_name: 代理名称
        api_type: API类型
        endpoint: API端点
        params: API参数
        """
        # 清理参数，移除敏感信息
        clean_params = self._sanitize_params(params)

        api_call_data = {
            "type": "api_call",
            "source": agent_name,
            "target": "API",
            "content": {
                "api_type": api_type,
                "endpoint": endpoint,
                "params": clean_params
            },
            "timestamp": time.time()
        }

        # 保存API调用历史
        self.api_calls.append(api_call_data)
        if len(self.api_calls) > self.max_history:
            self.api_calls.pop(0)

        self._broadcast(api_call_data)
        
        # 添加延时
        if self.delay_time > 0:
            time.sleep(self.delay_time)

    def intercept_api_response(self, agent_name: str, api_type: str, response: Any):
        """
        拦截API响应

        参数:
        agent_name: 代理名称
        api_type: API类型
        response: API响应
        """
        api_response_data = {
            "type": "api_response",
            "source": "API",
            "target": agent_name,
            "content": {
                "api_type": api_type,
                "response": self._format_content(response)
            },
            "timestamp": time.time()
        }

        # 保存API响应历史
        self.api_calls.append(api_response_data)
        if len(self.api_calls) > self.max_history:
            self.api_calls.pop(0)

        self._broadcast(api_response_data)
        
        # 添加延时
        if self.delay_time > 0:
            time.sleep(self.delay_time)

    def get_messages(self) -> List[Dict[str, Any]]:
        """
        获取消息历史

        返回:
        List[Dict[str, Any]]: 消息历史记录
        """
        return self.messages

    def get_api_calls(self) -> List[Dict[str, Any]]:
        """
        获取API调用历史

        返回:
        List[Dict[str, Any]]: API调用历史记录
        """
        return self.api_calls

    def _broadcast(self, message: Any):
        """
        广播消息给所有客户端

        参数:
        message: 消息内容
        """
        if self._broadcast_func:
            try:
                # 确保消息是JSON格式
                if isinstance(message, dict):
                    self._broadcast_func(json.dumps(message))
                else:
                    self._broadcast_func(message)
            except Exception as e:
                print(f"广播消息时出错: {str(e)}")

    def _format_content(self, content: Any) -> str:
        """
        格式化消息内容

        参数:
        content: 原始内容

        返回:
        str: 格式化后的内容
        """
        if isinstance(content, str):
            return content

        try:
            if isinstance(content, dict) or isinstance(content, list):
                return json.dumps(content, ensure_ascii=False)
            return str(content)
        except Exception:
            return str(content)

    def _sanitize_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        清理参数，移除敏感信息

        参数:
        params: 原始参数

        返回:
        Dict[str, Any]: 清理后的参数
        """
        if not params:
            return {}

        clean_params = params.copy()

        # 处理API密钥
        if 'api_key' in clean_params:
            key = clean_params['api_key']
            if isinstance(key, str) and len(key) > 8:
                # 保留前4位和后4位，中间用*替换
                clean_params['api_key'] = key[:4] + '*' * (len(key) - 8) + key[-4:]

        return clean_params

# 创建全局拦截器实例
interceptor = AgentInterceptor()
