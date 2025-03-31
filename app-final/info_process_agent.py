from base_agent import BaseAgent
import time
import json

class InfoProcessAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="InfoProcessAgent")
        self.target_agents = []
    
    def register_agent(self, agent):
        """注册接收信息的Agent"""
        if agent not in self.target_agents:
            self.target_agents.append(agent)
            self.log_action("注册代理", f"{agent.name}")
    
    def receive_message(self, message):
        """接收消息"""
        self.log_action("接收消息", f"类型: {message['type']}")
        if message["type"] == "request_info_update":
            return self.update_info()
        return {"status": "error", "message": "未支持的消息类型"}
    
    def update_info(self):
        """更新信息并分发给已注册的代理"""
        self.log_action("开始更新信息")
        # 获取市场信息
        market_info = self._fetch_market_info()
        transaction_info = self._fetch_transaction_info()
        whale_activity = self._fetch_whale_activity()
        contract_activity = self._fetch_contract_activity()
        coin_info = self._fetch_coin_info()
        
        # 整合所有信息
        all_info = {
            "market_info": market_info,
            "transaction_info": transaction_info,
            "whale_activity": whale_activity,
            "contract_activity": contract_activity,
            "coin_info": coin_info,
            "timestamp": time.time()
        }
        
        # 向所有注册的Agent分发信息
        self.log_action("分发信息", f"给 {len(self.target_agents)} 个代理")
        for agent in self.target_agents:
            try:
                message = self.create_mcp_message("info_update", all_info)
                self.send_message(agent, message)
            except Exception as e:
                self.log_action("错误", f"向 {agent.name} 分发信息失败: {str(e)}")
        
        return {"status": "success", "message": "信息已更新并分发"}
    
    def process(self, data=None):
        """处理数据请求"""
        return self.update_info()
    
    def _fetch_market_info(self):
        """获取市场信息"""
        self.log_action("获取市场信息")
        try:
            # 获取ETH价格
            eth_price_params = {
                "module": "stats", 
                "action": "ethprice"
            }
            eth_price = self.api_caller.call_blockchain_api("ethprice", eth_price_params)
            
            # 获取Gas价格
            gas_price_params = {
                "module": "gastracker", 
                "action": "gasoracle"
            }
            gas_price = self.api_caller.call_blockchain_api("gasoracle", gas_price_params)
            
            return {
                "eth_price": eth_price,
                "gas_price": gas_price
            }
        except Exception as e:
            self.log_action("错误", f"获取市场信息失败: {str(e)}")
            return {"error": f"获取市场信息失败: {str(e)}"}
    
    def _fetch_transaction_info(self):
        """获取交易信息"""
        self.log_action("获取交易信息")
        try:
            # 获取最新区块
            block_params = {
                "module": "proxy",
                "action": "eth_blockNumber"
            }
            latest_block = self.api_caller.call_blockchain_api("eth_blockNumber", block_params)
            
            # 获取最新交易
            tx_params = {
                "module": "account",
                "action": "txlist",
                "address": "0xaa7a9ca87d3694b5755f213b5d04094b8d0f0a6f", # 示例地址，可以更改
                "startblock": "0",
                "endblock": "99999999",
                "sort": "desc",
                "page": "1",
                "offset": "10"
            }
            latest_transactions = self.api_caller.call_blockchain_api("txlist", tx_params)
            
            # 由于缺少真实的API密钥，可能会返回错误，这里提供模拟数据
            if "error" in latest_transactions or (isinstance(latest_transactions, dict) and "result" in latest_transactions and latest_transactions["result"] == "Error! Invalid API Key"):
                self.log_action("警告", "使用模拟交易数据")
                latest_transactions = {
                    "status": "1",
                    "message": "OK",
                    "result": [
                        {
                            "blockNumber": "15483736",
                            "timeStamp": "1650123456",
                            "hash": "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
                            "from": "0x1234567890123456789012345678901234567890",
                            "to": "0xabcdef1234567890abcdef1234567890abcdef12",
                            "value": "1000000000000000000",  # 1 ETH
                            "gas": "21000",
                            "gasPrice": "50000000000"
                        },
                        {
                            "blockNumber": "15483735",
                            "timeStamp": "1650123446",
                            "hash": "0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
                            "from": "0xabcdef1234567890abcdef1234567890abcdef12",
                            "to": "0x2345678901234567890123456789012345678901",
                            "value": "2000000000000000000",  # 2 ETH
                            "gas": "21000",
                            "gasPrice": "50000000000"
                        }
                    ]
                }
            
            return {
                "latest_block": latest_block,
                "latest_transactions": latest_transactions
            }
        except Exception as e:
            self.log_action("错误", f"获取交易信息失败: {str(e)}")
            return {"error": f"获取交易信息失败: {str(e)}"}
    
    def _fetch_whale_activity(self):
        """获取大额交易活动"""
        self.log_action("获取大额交易活动")
        try:
            # 获取最近的大额交易
            whale_params = {
                "module": "account",
                "action": "txlist",
                "sort": "desc",
                "page": "1",
                "offset": "50"
            }
            transactions = self.api_caller.call_blockchain_api("txlist", whale_params)
            
            # 同样提供模拟数据
            if "error" in transactions or (isinstance(transactions, dict) and "result" in transactions and transactions["result"] == "Error! Invalid API Key"):
                self.log_action("警告", "使用模拟鲸鱼交易数据")
                transactions = {
                    "status": "1",
                    "message": "OK",
                    "result": [
                        {
                            "blockNumber": "15483736",
                            "timeStamp": "1650123456",
                            "hash": "0xwhale1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
                            "from": "0xwhale567890123456789012345678901234567890",
                            "to": "0xexchange234567890abcdef1234567890abcdef12",
                            "value": "5000000000000000000000",  # 5000 ETH
                            "gas": "21000",
                            "gasPrice": "50000000000"
                        },
                        {
                            "blockNumber": "15483735",
                            "timeStamp": "1650123446",
                            "hash": "0xwhale5ef1234567890abcdef1234567890abcdef1234567890abcdef1234567",
                            "from": "0xexchange34567890abcdef1234567890abcdef12",
                            "to": "0xwallet678901234567890123456789012345678901",
                            "value": "3000000000000000000000",  # 3000 ETH
                            "gas": "21000",
                            "gasPrice": "50000000000"
                        }
                    ]
                }
            
            # 过滤大额交易
            whale_txs = []
            if "result" in transactions and isinstance(transactions["result"], list):
                for tx in transactions["result"]:
                    # 假设大于1000 ETH的交易为大额交易
                    if float(tx.get("value", 0)) / 1e18 > 1000:
                        whale_txs.append(tx)
            
            return {
                "whale_transactions": whale_txs[:10] # 仅返回前10条
            }
        except Exception as e:
            self.log_action("错误", f"获取大额交易活动失败: {str(e)}")
            return {"error": f"获取大额交易活动失败: {str(e)}"}
    
    def _fetch_contract_activity(self):
        """获取合约活动"""
        self.log_action("获取合约活动")
        try:
            # 获取最新的合约交互
            contract_params = {
                "module": "account",
                "action": "txlistinternal",
                "sort": "desc",
                "page": "1",
                "offset": "10"
            }
            contract_activity = self.api_caller.call_blockchain_api("txlistinternal", contract_params)
            
            # 获取热门合约
            popular_contract_params = {
                "module": "stats",
                "action": "tokensupply",
                "contractaddress": "0xdac17f958d2ee523a2206206994597c13d831ec7" # USDT合约地址
            }
            token_supply = self.api_caller.call_blockchain_api("tokensupply", popular_contract_params)
            
            # 同样提供模拟数据
            if "error" in contract_activity or (isinstance(contract_activity, dict) and "result" in contract_activity and contract_activity["result"] == "Error! Invalid API Key"):
                self.log_action("警告", "使用模拟合约活动数据")
                contract_activity = {
                    "status": "1",
                    "message": "OK",
                    "result": [
                        {
                            "blockNumber": "15483736",
                            "timeStamp": "1650123456",
                            "hash": "0xcontract1234567890abcdef1234567890abcdef1234567890abcdef12345678",
                            "from": "0xuser1234567890123456789012345678901234567890",
                            "to": "0xdac17f958d2ee523a2206206994597c13d831ec7",  # USDT合约
                            "value": "0",
                            "gas": "100000",
                            "gasPrice": "50000000000",
                            "input": "0xa9059cbb000000000000000000000000abcdef123456789012345678901234567890abcd00000000000000000000000000000000000000000000000000000000000f4240"  # transfer
                        }
                    ]
                }
            
            if "error" in token_supply or (isinstance(token_supply, dict) and "result" in token_supply and token_supply["result"] == "Error! Invalid API Key"):
                token_supply = {"result": "78956802271.407929"}
            
            return {
                "contract_activity": contract_activity,
                "token_supply": token_supply
            }
        except Exception as e:
            self.log_action("错误", f"获取合约活动失败: {str(e)}")
            return {"error": f"获取合约活动失败: {str(e)}"}
    
    def _fetch_coin_info(self):
        """获取币种信息"""
        self.log_action("获取币种信息")
        try:
            # 获取Top代币列表
            # 注意：Etherscan API没有直接提供此功能，这里是一个示例
            # 实际应用中可能需要调用其他API
            tokens = [
                {"symbol": "ETH", "name": "Ethereum"},
                {"symbol": "USDT", "name": "Tether USD", "contract": "0xdac17f958d2ee523a2206206994597c13d831ec7"},
                {"symbol": "USDC", "name": "USD Coin", "contract": "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48"},
                {"symbol": "BNB", "name": "Binance Coin"},
                {"symbol": "MATIC", "name": "Polygon"}
            ]
            
            # 获取一些代币的价格信息
            # 从交易所API获取
            binance_ticker_params = {
                "symbol": "ETHUSDT"
            }
            eth_ticker = self.api_caller.call_exchange_api("binance", "/api/v3/ticker/price", binance_ticker_params)
            
            # 同样提供模拟数据
            if "error" in eth_ticker:
                self.log_action("警告", "使用模拟币价数据")
                eth_ticker = {"symbol": "ETHUSDT", "price": "3542.75"}
            
            return {
                "top_tokens": tokens,
                "price_info": {
                    "ETH": eth_ticker
                }
            }
        except Exception as e:
            self.log_action("错误", f"获取币种信息失败: {str(e)}")
            return {"error": f"获取币种信息失败: {str(e)}"} 