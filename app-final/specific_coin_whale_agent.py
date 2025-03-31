from base_agent import BaseAgent

class SpecificCoinWhaleAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="SpecificCoinWhaleAgent")
        self.data_clean_agent = None
        self.latest_info = {}
        self.tracked_coins = ["ETH", "USDT", "USDC"]  # 默认跟踪的币种
    
    def set_data_clean_agent(self, agent):
        """设置DataClean Agent"""
        self.data_clean_agent = agent
    
    def set_tracked_coins(self, coins):
        """设置要跟踪的币种"""
        if isinstance(coins, list):
            self.tracked_coins = coins
    
    def receive_message(self, message):
        """接收消息"""
        if message["type"] == "info_update":
            return self.process_info_update(message["content"])
        elif message["type"] == "track_coin":
            if "coin" in message["content"]:
                self.set_tracked_coins([message["content"]["coin"]])
            return {"status": "success", "message": f"现在跟踪币种: {self.tracked_coins}"}
        elif message["type"] == "request_whale_analysis":
            return self.analyze_whale_activity(message["content"])
        return {"status": "error", "message": "未支持的消息类型"}
    
    def process_info_update(self, info):
        """处理更新的信息"""
        self.latest_info = info
        
        # 处理市场信息中的大额持有者相关数据
        whale_data = self._extract_whale_data(info)
        
        # 如果有DataClean Agent，将处理后的数据发送给它
        if self.data_clean_agent:
            message = self.create_mcp_message("processed_data", {
                "type": "whale_activities",
                "data": whale_data
            })
            self.send_message(self.data_clean_agent, message)
        
        return {"status": "success", "message": "鲸鱼活动信息已处理"}
    
    def process(self, data=None):
        """处理任务"""
        if not data:
            return {"status": "error", "message": "未提供数据"}
        
        if "type" in data and data["type"] == "analyze_whale":
            return self.analyze_whale_activity(data.get("params", {}))
        
        return {"status": "error", "message": "未支持的任务类型"}
    
    def analyze_whale_activity(self, params):
        """分析鲸鱼活动"""
        if not self.latest_info:
            return {"status": "error", "message": "没有最新的市场信息"}
        
        coin = params.get("coin", self.tracked_coins[0] if self.tracked_coins else "ETH")
        
        # 使用LLM分析鲸鱼活动
        whale_txs = self.latest_info.get("whale_activity", {}).get("whale_transactions", [])
        
        if not whale_txs:
            return {"status": "warning", "message": "没有检测到鲸鱼交易"}
        
        # 提取前5个鲸鱼交易详情
        whale_details = []
        for tx in whale_txs[:5]:
            amount = float(tx.get("value", 0)) / 1e18
            whale_details.append({
                "from": tx.get("from", "unknown"),
                "to": tx.get("to", "unknown"),
                "amount": amount,
                "hash": tx.get("hash", "unknown"),
                "timestamp": tx.get("timeStamp", "unknown")
            })
        
        # 构建分析提示
        analysis_prompt = f"""
        分析以下{coin}鲸鱼交易数据，找出可能的趋势和意图:
        
        鲸鱼交易: {whale_details}
        
        请回答以下问题:
        1. 这些鲸鱼交易表明了什么市场趋势？
        2. 这些大额交易的地址是否有已知的关联（例如是否属于交易所、投资基金等）？
        3. 这些交易可能对{coin}的价格有什么短期影响？
        4. 你认为这些鲸鱼的行为是积累还是分发？
        
        请返回你的分析结果，格式为<output>分析结果</output>
        """
        
        analysis_result = self.call_llm(analysis_prompt)
        extracted_analysis = self.extract_output(analysis_result)
        
        return {
            "status": "success", 
            "coin": coin,
            "analysis": extracted_analysis
        }
    
    def _extract_whale_data(self, info):
        """从市场信息中提取鲸鱼相关数据"""
        whale_data = {
            "timestamp": info.get("timestamp", 0),
            "whale_transactions": []
        }
        
        # 提取大额交易
        whale_txs = info.get("whale_activity", {}).get("whale_transactions", [])
        
        # 过滤出我们关注的币种的交易
        # 实际应用中，这里可能需要更复杂的逻辑来识别特定代币的交易
        filtered_txs = []
        for tx in whale_txs:
            tx_data = {
                "from": tx.get("from", ""),
                "to": tx.get("to", ""),
                "value": tx.get("value", "0"),
                "hash": tx.get("hash", ""),
                "blockNumber": tx.get("blockNumber", ""),
                "timeStamp": tx.get("timeStamp", ""),
            }
            
            # 使用LLM判断这笔交易的币种
            prompt = f"""
            根据以下交易信息，判断这可能是哪种加密货币的交易:
            
            发送方: {tx_data['from']}
            接收方: {tx_data['to']}
            金额: {float(tx_data['value']) / 1e18 if tx_data['value'].isdigit() else tx_data['value']}
            
            请从以下选项中选择一个: {', '.join(self.tracked_coins)}
            
            请只返回币种符号，格式为<output>币种符号</output>
            """
            
            result = self.call_llm(prompt)
            coin = self.extract_output(result)
            
            if coin in self.tracked_coins:
                tx_data["detected_coin"] = coin
                filtered_txs.append(tx_data)
        
        whale_data["whale_transactions"] = filtered_txs
        
        return whale_data 