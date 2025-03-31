import json
import time
from abc import ABC, abstractmethod
from api_caller import APICaller

class BaseAgent(ABC):
    def __init__(self, name):
        self.name = name
        self.api_caller = APICaller()
        self.config = self._load_config()
    
    def _load_config(self):
        """加载配置文件"""
        config = {}
        with open("config.txt", "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    try:
                        key, value = line.split("=", 1)
                        config[key.strip()] = value.strip().strip('"').strip("'")
                    except ValueError:
                        continue
        return config
    
    def call_llm(self, prompt):
        """调用大语言模型"""
        response = self.api_caller.call_llm_api(prompt)
        if self.config.get("DEBUG_SLEEP", "0") == "1":
            time.sleep(1)
        return response
    
    def extract_output(self, response, tag="o"):
        """从LLM响应中提取标签内容"""
        start_tag = f"<{tag}>"
        end_tag = f"</{tag}>"
        if start_tag in response and end_tag in response:
            start_idx = response.find(start_tag) + len(start_tag)
            end_idx = response.find(end_tag)
            return response[start_idx:end_idx].strip()
        return response
    
    def create_mcp_message(self, message_type, content):
        """创建MCP协议消息"""
        return {
            "agent": self.name,
            "type": message_type,
            "content": content,
            "timestamp": time.time()
        }
    
    def send_message(self, target_agent, message):
        """发送消息到目标Agent"""
        # 调试输出代理间通信
        if self.config.get("DEBUG_MODE") == "True":
            print(f"🔄 [{self.name}] -> [{target_agent.name}]: {message['type']}")
        
        return target_agent.receive_message(message)
    
    def log_action(self, action, details=None):
        """记录代理执行动作"""
        if self.config.get("DEBUG_MODE") == "True":
            if details:
                print(f"🔍 [{self.name}] {action}: {details}")
            else:
                print(f"🔍 [{self.name}] {action}")
    
    @abstractmethod
    def receive_message(self, message):
        """接收消息的抽象方法"""
        pass
    
    @abstractmethod
    def process(self, data=None):
        """处理任务的抽象方法"""
        pass 