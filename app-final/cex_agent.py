from base_agent import BaseAgent

class CEXAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="CEXAgent")
        self.central_agent = None
        self.active_exchange = None
        self.api_keys = {}
    
    def set_central_agent(self, agent):
        """设置Central Agent"""
        self.central_agent = agent
    
    def receive_message(self, message):
        """接收消息"""
        if message["type"] == "set_exchange":
            return self.set_exchange(message["content"])
        elif message["type"] == "place_order":
            return self.place_order(message["content"])
        elif message["type"] == "cancel_order":
            return self.cancel_order(message["content"])
        elif message["type"] == "get_balance":
            return self.get_balance(message["content"])
        elif message["type"] == "get_market_data":
            return self.get_market_data(message["content"])
        return {"status": "error", "message": "未支持的消息类型"}
    
    def process(self, data=None):
        """处理任务"""
        if not data:
            return {"status": "error", "message": "未提供数据"}
        
        if "type" in data:
            if data["type"] == "set_exchange":
                return self.set_exchange(data.get("params", {}))
            elif data["type"] == "place_order":
                return self.place_order(data.get("params", {}))
            elif data["type"] == "cancel_order":
                return self.cancel_order(data.get("params", {}))
            elif data["type"] == "get_balance":
                return self.get_balance(data.get("params", {}))
            elif data["type"] == "get_market_data":
                return self.get_market_data(data.get("params", {}))
        
        return {"status": "error", "message": "未支持的任务类型"}
    
    def set_exchange(self, params):
        """设置活动交易所"""
        if "exchange" not in params:
            return {"status": "error", "message": "缺少交易所名称"}
        
        exchange = params["exchange"].lower()
        api_key = params.get("api_key", self.config.get(f"{exchange.upper()}_API_KEY"))
        api_secret = params.get("api_secret", self.config.get(f"{exchange.upper()}_API_SECRET"))
        
        if not api_key or not api_secret:
            return {"status": "error", "message": "缺少API密钥"}
        
        # 保存交易所设置
        self.active_exchange = exchange
        self.api_keys[exchange] = {
            "api_key": api_key,
            "api_secret": api_secret
        }
        
        return {
            "status": "success",
            "message": f"已设置活动交易所: {exchange}",
            "exchange": exchange
        }
    
    def place_order(self, params):
        """下单"""
        if not self.active_exchange:
            return {"status": "error", "message": "未设置活动交易所"}
        
        if "symbol" not in params or "side" not in params or "type" not in params:
            return {"status": "error", "message": "缺少必要的订单参数"}
        
        symbol = params["symbol"]
        side = params["side"]  # buy or sell
        order_type = params["type"]  # limit, market, etc.
        quantity = params.get("quantity")
        price = params.get("price")
        
        # 构建API参数
        api_params = {
            "symbol": symbol,
            "side": side.upper(),
            "type": order_type.upper()
        }
        
        if quantity:
            api_params["quantity"] = quantity
        
        if price and order_type.lower() == "limit":
            api_params["price"] = price
        
        # 根据不同交易所构建不同的API调用
        try:
            if self.active_exchange == "binance":
                endpoint = "/api/v3/order"
                response = self.api_caller.call_exchange_api(
                    "binance", 
                    endpoint, 
                    api_params, 
                    method="POST"
                )
            else:
                return {"status": "error", "message": f"不支持的交易所: {self.active_exchange}"}
            
            # 检查API响应
            if "error" in response:
                return {"status": "error", "message": response["error"]}
            
            # 解析订单信息
            order_id = response.get("orderId", "unknown")
            
            # 回报执行结果给中央代理
            if self.central_agent:
                result = {
                    "exchange": self.active_exchange,
                    "order_id": order_id,
                    "symbol": symbol,
                    "side": side,
                    "type": order_type,
                    "quantity": quantity,
                    "price": price,
                    "status": "placed"
                }
                message = self.create_mcp_message("command_execution_result", result)
                self.send_message(self.central_agent, message)
            
            return {
                "status": "success",
                "message": f"订单已提交",
                "order_id": order_id,
                "details": response
            }
        except Exception as e:
            return {"status": "error", "message": f"下单失败: {str(e)}"}
    
    def cancel_order(self, params):
        """取消订单"""
        if not self.active_exchange:
            return {"status": "error", "message": "未设置活动交易所"}
        
        if "symbol" not in params or "order_id" not in params:
            return {"status": "error", "message": "缺少必要的取消参数"}
        
        symbol = params["symbol"]
        order_id = params["order_id"]
        
        # 构建API参数
        api_params = {
            "symbol": symbol,
            "orderId": order_id
        }
        
        # 根据不同交易所构建不同的API调用
        try:
            if self.active_exchange == "binance":
                endpoint = "/api/v3/order"
                response = self.api_caller.call_exchange_api(
                    "binance", 
                    endpoint, 
                    api_params, 
                    method="DELETE"
                )
            else:
                return {"status": "error", "message": f"不支持的交易所: {self.active_exchange}"}
            
            # 检查API响应
            if "error" in response:
                return {"status": "error", "message": response["error"]}
            
            # 回报执行结果给中央代理
            if self.central_agent:
                result = {
                    "exchange": self.active_exchange,
                    "order_id": order_id,
                    "symbol": symbol,
                    "status": "cancelled"
                }
                message = self.create_mcp_message("command_execution_result", result)
                self.send_message(self.central_agent, message)
            
            return {
                "status": "success",
                "message": f"订单已取消",
                "details": response
            }
        except Exception as e:
            return {"status": "error", "message": f"取消订单失败: {str(e)}"}
    
    def get_balance(self, params):
        """获取账户余额"""
        if not self.active_exchange:
            return {"status": "error", "message": "未设置活动交易所"}
        
        # 构建API参数
        api_params = {}
        
        # 根据不同交易所构建不同的API调用
        try:
            if self.active_exchange == "binance":
                endpoint = "/api/v3/account"
                response = self.api_caller.call_exchange_api(
                    "binance", 
                    endpoint, 
                    api_params
                )
            else:
                return {"status": "error", "message": f"不支持的交易所: {self.active_exchange}"}
            
            # 检查API响应
            if "error" in response:
                return {"status": "error", "message": response["error"]}
            
            # 解析余额信息
            balances = []
            if "balances" in response:
                for balance in response["balances"]:
                    if float(balance.get("free", 0)) > 0 or float(balance.get("locked", 0)) > 0:
                        balances.append({
                            "asset": balance.get("asset", ""),
                            "free": float(balance.get("free", 0)),
                            "locked": float(balance.get("locked", 0))
                        })
            
            return {
                "status": "success",
                "exchange": self.active_exchange,
                "balances": balances
            }
        except Exception as e:
            return {"status": "error", "message": f"获取余额失败: {str(e)}"}
    
    def get_market_data(self, params):
        """获取市场数据"""
        if "symbol" not in params:
            return {"status": "error", "message": "缺少交易对参数"}
        
        symbol = params["symbol"]
        exchange = params.get("exchange", self.active_exchange)
        
        if not exchange:
            return {"status": "error", "message": "未指定交易所"}
        
        data_type = params.get("type", "ticker")  # ticker, orderbook, kline
        
        # 根据不同数据类型构建不同的API调用
        try:
            if exchange.lower() == "binance":
                if data_type == "ticker":
                    endpoint = "/api/v3/ticker/price"
                    api_params = {"symbol": symbol}
                    response = self.api_caller.call_exchange_api("binance", endpoint, api_params)
                elif data_type == "orderbook":
                    endpoint = "/api/v3/depth"
                    api_params = {"symbol": symbol, "limit": params.get("limit", 20)}
                    response = self.api_caller.call_exchange_api("binance", endpoint, api_params)
                elif data_type == "kline":
                    endpoint = "/api/v3/klines"
                    api_params = {
                        "symbol": symbol,
                        "interval": params.get("interval", "1h"),
                        "limit": params.get("limit", 100)
                    }
                    response = self.api_caller.call_exchange_api("binance", endpoint, api_params)
                else:
                    return {"status": "error", "message": f"不支持的数据类型: {data_type}"}
            else:
                return {"status": "error", "message": f"不支持的交易所: {exchange}"}
            
            # 检查API响应
            if "error" in response:
                return {"status": "error", "message": response["error"]}
            
            return {
                "status": "success",
                "exchange": exchange,
                "symbol": symbol,
                "type": data_type,
                "data": response
            }
        except Exception as e:
            return {"status": "error", "message": f"获取市场数据失败: {str(e)}"} 