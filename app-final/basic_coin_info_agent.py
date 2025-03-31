from base_agent import BaseAgent

class BasicCoinInfoAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="BasicCoinInfoAgent")
        self.data_clean_agent = None
        self.latest_info = {}
        self.coin_data = {}  # 存储币种信息
    
    def set_data_clean_agent(self, agent):
        """设置DataClean Agent"""
        self.data_clean_agent = agent
    
    def receive_message(self, message):
        """接收消息"""
        if message["type"] == "info_update":
            return self.process_info_update(message["content"])
        elif message["type"] == "get_coin_info":
            if "coin" in message["content"]:
                return self.get_coin_info(message["content"]["coin"])
            else:
                return {"status": "error", "message": "未提供币种"}
        elif message["type"] == "request_market_analysis":
            return self.analyze_market_data(message["content"])
        return {"status": "error", "message": "未支持的消息类型"}
    
    def process_info_update(self, info):
        """处理更新的信息"""
        self.latest_info = info
        
        # 处理市场信息中的币种信息
        coin_info_data = self._extract_coin_info(info)
        
        # 更新币种数据
        for coin in coin_info_data["coins"]:
            symbol = coin["symbol"]
            self.coin_data[symbol] = coin
        
        # 如果有DataClean Agent，将处理后的数据发送给它
        if self.data_clean_agent:
            message = self.create_mcp_message("processed_data", {
                "type": "basic_coin_info",
                "data": coin_info_data
            })
            self.send_message(self.data_clean_agent, message)
        
        return {"status": "success", "message": "币种信息已处理"}
    
    def process(self, data=None):
        """处理任务"""
        if not data:
            return {"status": "error", "message": "未提供数据"}
        
        if "type" in data and data["type"] == "get_coin_info":
            if "coin" in data:
                return self.get_coin_info(data["coin"])
            else:
                return {"status": "error", "message": "未提供币种"}
        elif "type" in data and data["type"] == "analyze_market":
            return self.analyze_market_data(data.get("params", {}))
        
        return {"status": "error", "message": "未支持的任务类型"}
    
    def get_coin_info(self, coin_symbol):
        """获取特定币种的信息"""
        if coin_symbol in self.coin_data:
            return {
                "status": "success",
                "coin_info": self.coin_data[coin_symbol]
            }
        else:
            return {
                "status": "error",
                "message": f"没有找到币种 {coin_symbol} 的信息"
            }
    
    def analyze_market_data(self, params=None):
        """分析市场数据"""
        if not self.latest_info:
            return {"status": "error", "message": "没有最新的市场信息"}
        
        # 获取市场信息
        market_info = self.latest_info.get("market_info", {})
        
        # 获取币种信息
        coin_info = self.latest_info.get("coin_info", {})
        
        # 使用LLM分析市场情况
        analysis_prompt = f"""
        分析以下加密货币市场数据:
        
        市场数据: {market_info}
        币种数据: {coin_info}
        
        请回答以下问题:
        1. 当前市场整体趋势如何？
        2. ETH价格表现如何？
        3. 有哪些值得关注的币种表现？
        4. 根据Gas费的情况，网络拥堵程度如何？
        5. 推荐的短期投资策略是什么？
        
        请返回你的分析结果，格式为<output>分析结果</output>
        """
        
        analysis_result = self.call_llm(analysis_prompt)
        extracted_analysis = self.extract_output(analysis_result)
        
        return {
            "status": "success", 
            "analysis": extracted_analysis
        }
    
    def _extract_coin_info(self, info):
        """从市场信息中提取币种信息"""
        coin_info_data = {
            "timestamp": info.get("timestamp", 0),
            "coins": []
        }
        
        # 从币种信息中提取代币列表
        top_tokens = info.get("coin_info", {}).get("top_tokens", [])
        price_info = info.get("coin_info", {}).get("price_info", {})
        
        # 处理每个代币的信息
        for token in top_tokens:
            symbol = token.get("symbol", "")
            
            # 构建币种基本信息
            coin_data = {
                "symbol": symbol,
                "name": token.get("name", ""),
                "contract": token.get("contract", ""),
                "price": None,
                "market_cap": None,
                "volume_24h": None,
                "change_24h": None
            }
            
            # 如果有价格信息，添加价格
            if symbol in price_info:
                price_data = price_info[symbol]
                if isinstance(price_data, dict) and "price" in price_data:
                    coin_data["price"] = price_data["price"]
            
            # 使用LLM补充币种信息
            if symbol in ["ETH", "USDT", "USDC"]:  # 仅为主要币种生成额外信息
                prompt = f"""
                根据你的知识，请提供以下加密货币的基本信息:
                
                币种: {symbol} ({token.get("name", "")})
                
                请简要回答以下问题:
                1. 这个币种的主要用途是什么?
                2. 它是哪个区块链的原生代币?
                3. 它的主要特点是什么?
                
                请返回一个JSON格式的回答，包含"description"和"features"两个字段，格式为<output>{{your json}}</output>
                """
                
                result = self.call_llm(prompt)
                try:
                    # 尝试解析LLM返回的JSON
                    extracted_info = self.extract_output(result)
                    import json
                    extra_info = json.loads(extracted_info)
                    
                    if isinstance(extra_info, dict):
                        for key, value in extra_info.items():
                            coin_data[key] = value
                except:
                    # 如果解析失败，添加原始文本
                    coin_data["extra_info"] = self.extract_output(result)
            
            # 添加到币种数据列表
            coin_info_data["coins"].append(coin_data)
        
        return coin_info_data 