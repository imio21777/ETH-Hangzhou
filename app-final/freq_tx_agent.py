from base_agent import BaseAgent
from collections import defaultdict
import json

class FreqTxAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="FreqTxAgent")
        self.data_clean_agent = None
        self.latest_info = {}
        self.transaction_history = defaultdict(list)  # 地址 -> 交易列表
        self.frequency_threshold = 5  # 短时间内超过这个数量视为高频
    
    def set_data_clean_agent(self, agent):
        """设置DataClean Agent"""
        self.data_clean_agent = agent
    
    def set_frequency_threshold(self, threshold):
        """设置频率阈值"""
        if isinstance(threshold, int) and threshold > 0:
            self.frequency_threshold = threshold
    
    def receive_message(self, message):
        """接收消息"""
        try:
            self.log_action("接收消息", f"类型: {message['type']}")
            
            if message["type"] == "info_update":
                # 确保内容是字典类型
                content = message["content"]
                if isinstance(content, str):
                    self.log_action("警告", f"收到字符串内容，尝试解析JSON: {content[:100]}...")
                    try:
                        content = json.loads(content)
                    except Exception as e:
                        self.log_action("错误", f"JSON解析失败: {str(e)}")
                        content = {}  # 如果解析失败，使用空字典
                
                return self.process_info_update(content)
            elif message["type"] == "set_threshold":
                if "threshold" in message["content"]:
                    self.set_frequency_threshold(message["content"]["threshold"])
                return {"status": "success", "message": f"频率阈值设置为: {self.frequency_threshold}"}
            elif message["type"] == "request_freq_analysis":
                return self.analyze_frequent_transactions(message["content"])
            
            return {"status": "error", "message": "未支持的消息类型"}
        except Exception as e:
            self.log_action("错误", f"处理消息失败: {str(e)}")
            return {"status": "error", "message": f"处理消息失败: {str(e)}"}
    
    def process_info_update(self, info):
        """处理更新的信息"""
        try:
            self.log_action("处理更新的信息")
            self.latest_info = info
            
            # 处理市场信息中的频繁交易数据
            freq_tx_data = self._extract_frequent_tx_data(info)
            
            # 如果有DataClean Agent，将处理后的数据发送给它
            if self.data_clean_agent:
                message = self.create_mcp_message("processed_data", {
                    "type": "frequent_transactions",
                    "data": freq_tx_data
                })
                self.send_message(self.data_clean_agent, message)
            
            return {"status": "success", "message": "频繁交易信息已处理"}
        except Exception as e:
            self.log_action("错误", f"处理信息更新失败: {str(e)}")
            return {"status": "error", "message": f"处理信息更新失败: {str(e)}"}
    
    def process(self, data=None):
        """处理任务"""
        if not data:
            return {"status": "error", "message": "未提供数据"}
        
        if "type" in data and data["type"] == "analyze_freq_tx":
            return self.analyze_frequent_transactions(data.get("params", {}))
        
        return {"status": "error", "message": "未支持的任务类型"}
    
    def analyze_frequent_transactions(self, params):
        """分析频繁交易"""
        if not self.latest_info:
            return {"status": "error", "message": "没有最新的市场信息"}
        
        address = params.get("address", None)
        
        # 如果没有指定地址，则分析所有高频交易地址
        if not address:
            # 获取交易频率最高的地址
            frequent_addresses = self._get_frequent_addresses()
            if not frequent_addresses:
                return {"status": "warning", "message": "没有检测到高频交易地址"}
            
            # 使用前三个高频地址作为样本
            sample_addresses = frequent_addresses[:3]
        else:
            # 使用指定的地址
            if address in self.transaction_history:
                sample_addresses = [address]
            else:
                return {"status": "warning", "message": f"地址 {address} 没有交易记录"}
        
        # 构建地址交易数据
        address_data = []
        for addr in sample_addresses:
            txs = self.transaction_history[addr]
            address_data.append({
                "address": addr,
                "transaction_count": len(txs),
                "recent_transactions": txs[:5]  # 最近5笔交易
            })
        
        # 使用LLM分析高频交易行为
        analysis_prompt = f"""
        分析以下高频交易地址的行为特征:
        
        地址交易数据: {address_data}
        
        请回答以下问题:
        1. 这些高频交易地址可能属于什么类型的用户或实体（例如套利机器人、交易所、市场做市商等）？
        2. 这些高频交易的模式是什么？
        3. 这些交易行为可能对市场有什么影响？
        4. 是否存在可疑的交易行为？
        
        请返回你的分析结果，格式为<o>分析结果</o>
        """
        
        analysis_result = self.call_llm(analysis_prompt)
        extracted_analysis = self.extract_output(analysis_result)
        
        return {
            "status": "success", 
            "addresses": [addr["address"] for addr in address_data],
            "analysis": extracted_analysis
        }
    
    def _extract_frequent_tx_data(self, info):
        """从市场信息中提取频繁交易数据"""
        self.log_action("提取频繁交易数据")
        freq_tx_data = {
            "timestamp": info.get("timestamp", 0),
            "frequent_addresses": []
        }
        
        try:
            # 从交易信息中提取交易
            tx_info = info.get("transaction_info", {})
            if isinstance(tx_info, str):
                self.log_action("警告", f"交易信息为字符串: {tx_info[:100]}...")
                try:
                    tx_info = json.loads(tx_info)
                except Exception as e:
                    self.log_action("错误", f"交易信息JSON解析失败: {str(e)}")
                    tx_info = {}
            
            latest_tx = tx_info.get("latest_transactions", {})
            if isinstance(latest_tx, str):
                self.log_action("警告", f"最新交易为字符串: {latest_tx[:100]}...")
                try:
                    latest_tx = json.loads(latest_tx)
                except Exception as e:
                    self.log_action("错误", f"最新交易JSON解析失败: {str(e)}")
                    latest_tx = {}
            
            # 检查结果是否是字典而不是列表
            result = latest_tx.get("result", [])
            if isinstance(result, str):
                self.log_action("警告", f"交易结果为字符串: {result[:100]}...")
                try:
                    result = json.loads(result)
                except Exception as e:
                    self.log_action("错误", f"交易结果JSON解析失败: {str(e)}")
                    result = []
            
            # 确保结果是列表
            if not isinstance(result, list):
                self.log_action("警告", f"交易结果不是列表，而是 {type(result)}")
                result = []
            
            transactions = result
            self.log_action("获取交易数据", f"共 {len(transactions)} 条")
            
            # 更新交易历史
            for tx in transactions:
                if not isinstance(tx, dict):
                    self.log_action("警告", f"交易不是字典，而是 {type(tx)}")
                    continue
                
                from_addr = tx.get("from", "")
                to_addr = tx.get("to", "")
                
                if from_addr:
                    tx_data = {
                        "hash": tx.get("hash", ""),
                        "to": to_addr,
                        "value": tx.get("value", "0"),
                        "timeStamp": tx.get("timeStamp", ""),
                        "blockNumber": tx.get("blockNumber", ""),
                        "type": "send"
                    }
                    self.transaction_history[from_addr].append(tx_data)
                
                if to_addr:
                    tx_data = {
                        "hash": tx.get("hash", ""),
                        "from": from_addr,
                        "value": tx.get("value", "0"),
                        "timeStamp": tx.get("timeStamp", ""),
                        "blockNumber": tx.get("blockNumber", ""),
                        "type": "receive"
                    }
                    self.transaction_history[to_addr].append(tx_data)
            
            # 找出频繁交易的地址
            frequent_addresses = self._get_frequent_addresses()
            
            # 为每个高频地址添加数据
            for addr in frequent_addresses:
                txs = self.transaction_history[addr]
                freq_tx_data["frequent_addresses"].append({
                    "address": addr,
                    "transaction_count": len(txs),
                    "recent_transactions": txs[:10]  # 最近10笔交易
                })
            
            self.log_action("频繁交易地址", f"共 {len(freq_tx_data['frequent_addresses'])} 个")
        except Exception as e:
            self.log_action("错误", f"提取频繁交易数据失败: {str(e)}")
        
        return freq_tx_data
    
    def _get_frequent_addresses(self):
        """获取交易频繁的地址列表"""
        # 计算每个地址的交易频率
        address_frequency = {}
        for addr, txs in self.transaction_history.items():
            address_frequency[addr] = len(txs)
        
        # 按交易频率降序排序
        sorted_addresses = sorted(address_frequency.items(), key=lambda x: x[1], reverse=True)
        
        # 过滤出交易频率超过阈值的地址
        frequent_addresses = [addr for addr, freq in sorted_addresses if freq >= self.frequency_threshold]
        
        return frequent_addresses 