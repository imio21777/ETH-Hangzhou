from base_agent import BaseAgent
import json

class CEXWithdrawAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="CEXWithdrawAgent")
        self.data_clean_agent = None
        self.latest_info = {}
    
    def set_data_clean_agent(self, agent):
        """设置DataClean Agent"""
        self.data_clean_agent = agent
    
    def receive_message(self, message):
        """接收消息"""
        if message["type"] == "info_update":
            self.log_action("接收信息更新")
            return self.process_info_update(message["content"])
        elif message["type"] == "request_analysis":
            self.log_action("接收分析请求")
            return self.analyze_withdrawals(message["content"])
        return {"status": "error", "message": "未支持的消息类型"}
    
    def process_info_update(self, info):
        """处理更新的信息"""
        self.log_action("处理更新的信息")
        self.latest_info = info
        
        # 处理市场信息中的提款相关数据
        withdrawal_data = self._extract_withdrawal_data(info)
        
        # 如果有DataClean Agent，将处理后的数据发送给它
        if self.data_clean_agent:
            message = self.create_mcp_message("processed_data", {
                "type": "cex_withdrawals",
                "data": withdrawal_data
            })
            self.send_message(self.data_clean_agent, message)
        
        return {"status": "success", "message": "CEX提款信息已处理"}
    
    def process(self, data=None):
        """处理任务"""
        if not data:
            return {"status": "error", "message": "未提供数据"}
        
        if "type" in data and data["type"] == "analyze_withdrawals":
            return self.analyze_withdrawals(data["params"])
        
        return {"status": "error", "message": "未支持的任务类型"}
    
    def analyze_withdrawals(self, params):
        """分析提款情况"""
        self.log_action("分析提款情况")
        if not self.latest_info:
            return {"status": "error", "message": "没有最新的市场信息"}
        
        # 使用LLM分析提款趋势
        analysis_prompt = f"""
        分析以下区块链交易所提款数据，找出可能的趋势和异常:
        
        交易数据: {self.latest_info.get('transaction_info', {})}
        
        请回答以下问题:
        1. 最近是否有大规模的交易所提款?
        2. 与过去相比，提款趋势如何变化?
        3. 提款可能对市场价格有什么影响?
        
        请返回你的分析结果，格式为<o>分析结果</o>
        """
        
        analysis_result = self.call_llm(analysis_prompt)
        extracted_analysis = self.extract_output(analysis_result)
        
        return {
            "status": "success", 
            "analysis": extracted_analysis
        }
    
    def _extract_withdrawal_data(self, info):
        """从市场信息中提取提款相关数据"""
        self.log_action("提取提款相关数据")
        withdrawal_data = {
            "timestamp": info.get("timestamp", 0),
            "withdrawals": []
        }
        
        # 从交易信息中提取提款相关的交易
        try:
            tx_info = info.get("transaction_info", {})
            latest_tx = tx_info.get("latest_transactions", {})
            
            # 检查结果是否是字典而不是列表
            result = latest_tx.get("result", [])
            if isinstance(result, str):
                self.log_action("警告", f"交易数据为字符串: {result[:100]}...")
                # 尝试解析JSON字符串
                try:
                    result = json.loads(result)
                except:
                    result = []
            
            # 确保结果是列表
            if not isinstance(result, list):
                self.log_action("警告", f"交易数据不是列表，而是 {type(result)}")
                result = []
            
            transactions = result
            self.log_action("获取交易数据", f"共 {len(transactions)} 条")
            
            # 使用LLM识别可能的提款交易
            if transactions:
                # 取前5条交易作为示例
                sample_txs = transactions[:5]
                
                # 确保每个交易都是字典对象
                valid_txs = []
                for i, tx in enumerate(sample_txs):
                    if isinstance(tx, dict):
                        valid_txs.append(tx)
                    else:
                        self.log_action("警告", f"交易 #{i} 不是字典: {type(tx)}")
                
                if not valid_txs:
                    self.log_action("警告", "没有有效的交易数据")
                    return withdrawal_data
                
                # 生成交易描述
                tx_descriptions = []
                for i, tx in enumerate(valid_txs):
                    from_addr = tx.get('from', 'unknown')
                    to_addr = tx.get('to', 'unknown')
                    value = float(tx.get('value', 0)) / 1e18
                    tx_descriptions.append(f"交易#{i}: 地址: {from_addr} -> {to_addr}, 金额: {value} ETH")
                
                tx_descriptions_text = "\n".join(tx_descriptions)
                
                prompt = f"""
                以下是一些区块链交易，请识别哪些可能是交易所提款交易:
                
                {tx_descriptions_text}
                
                请列出可能是交易所提款的交易索引(从0开始)，格式为<o>[索引列表]</o>
                """
                
                result = self.call_llm(prompt)
                indices = self.extract_output(result)
                
                try:
                    # 尝试将输出解析为索引列表
                    if indices.startswith("[") and indices.endswith("]"):
                        indices = eval(indices)  # 安全起见，实际应用中应该使用json.loads
                    else:
                        indices = []
                    
                    # 提取对应的交易
                    for idx in indices:
                        if 0 <= idx < len(valid_txs):
                            withdrawal_data["withdrawals"].append(valid_txs[idx])
                            self.log_action("提取提款交易", f"交易#{idx}")
                except Exception as e:
                    self.log_action("错误", f"解析索引失败: {str(e)}")
                    # 解析失败时设置为空列表
                    withdrawal_data["withdrawals"] = []
        except Exception as e:
            self.log_action("错误", f"提取提款数据失败: {str(e)}")
            withdrawal_data["withdrawals"] = []
        
        return withdrawal_data 