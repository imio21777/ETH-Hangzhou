from base_agent import BaseAgent
import time

class AutoTradeAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="AutoTradeAgent")
        self.central_agent = None
        self.wallet_agent = None
        self.cex_agent = None
        self.strategies = {}  # 存储交易策略
    
    def set_agents(self, central_agent, wallet_agent, cex_agent):
        """设置关联的其他代理"""
        self.central_agent = central_agent
        self.wallet_agent = wallet_agent
        self.cex_agent = cex_agent
    
    def receive_message(self, message):
        """接收消息"""
        if message["type"] == "execute_trade":
            return self.execute_trade(message["content"])
        elif message["type"] == "add_strategy":
            return self.add_strategy(message["content"])
        elif message["type"] == "remove_strategy":
            return self.remove_strategy(message["content"])
        elif message["type"] == "list_strategies":
            return self.list_strategies()
        return {"status": "error", "message": "未支持的消息类型"}
    
    def process(self, data=None):
        """处理任务"""
        if not data:
            return {"status": "error", "message": "未提供数据"}
        
        if "type" in data:
            if data["type"] == "execute_trade":
                return self.execute_trade(data.get("params", {}))
            elif data["type"] == "add_strategy":
                return self.add_strategy(data.get("params", {}))
            elif data["type"] == "remove_strategy":
                return self.remove_strategy(data.get("params", {}))
            elif data["type"] == "list_strategies":
                return self.list_strategies()
        
        return {"status": "error", "message": "未支持的任务类型"}
    
    def execute_trade(self, params):
        """执行交易操作"""
        if "target" not in params or "action" not in params:
            return {"status": "error", "message": "缺少必要的交易参数"}
        
        target = params["target"]  # "cex" or "dex"
        action = params["action"]  # "buy", "sell", "approve", etc.
        
        if target == "cex":
            if not self.cex_agent:
                return {"status": "error", "message": "未设置CEX代理"}
            
            return self._execute_cex_trade(action, params)
        elif target == "dex":
            if not self.wallet_agent:
                return {"status": "error", "message": "未设置钱包代理"}
            
            return self._execute_dex_trade(action, params)
        else:
            return {"status": "error", "message": f"不支持的交易目标: {target}"}
    
    def add_strategy(self, params):
        """添加交易策略"""
        if "id" not in params or "description" not in params or "rules" not in params:
            return {"status": "error", "message": "缺少必要的策略参数"}
        
        strategy_id = params["id"]
        description = params["description"]
        rules = params["rules"]
        
        # 检查策略规则
        if not isinstance(rules, list) or not rules:
            return {"status": "error", "message": "策略规则必须是非空列表"}
        
        # 添加策略
        self.strategies[strategy_id] = {
            "description": description,
            "rules": rules,
            "active": params.get("active", True),
            "created_at": params.get("created_at", int(time.time()))
        }
        
        return {
            "status": "success",
            "message": f"已添加策略: {strategy_id}",
            "strategy": {
                "id": strategy_id,
                "description": description,
                "active": self.strategies[strategy_id]["active"]
            }
        }
    
    def remove_strategy(self, params):
        """移除交易策略"""
        if "id" not in params:
            return {"status": "error", "message": "缺少策略ID"}
        
        strategy_id = params["id"]
        
        if strategy_id in self.strategies:
            del self.strategies[strategy_id]
            return {
                "status": "success",
                "message": f"已移除策略: {strategy_id}"
            }
        
        return {
            "status": "error",
            "message": f"未找到策略: {strategy_id}"
        }
    
    def list_strategies(self):
        """列出所有交易策略"""
        strategy_list = []
        for strategy_id, strategy_data in self.strategies.items():
            strategy_list.append({
                "id": strategy_id,
                "description": strategy_data["description"],
                "active": strategy_data["active"],
                "created_at": strategy_data["created_at"]
            })
        
        return {
            "status": "success",
            "strategies": strategy_list
        }
    
    def _execute_cex_trade(self, action, params):
        """执行中心化交易所交易"""
        if action == "buy" or action == "sell":
            # 构建下单参数
            order_params = {
                "symbol": params.get("symbol"),
                "side": action,
                "type": params.get("order_type", "limit"),
                "quantity": params.get("quantity"),
                "price": params.get("price")
            }
            
            # 调用CEX代理下单
            message = self.create_mcp_message("place_order", order_params)
            result = self.send_message(self.cex_agent, message)
            
            # 回报结果给中央代理
            if self.central_agent and result.get("status") == "success":
                response = {
                    "operation": "cex_trade",
                    "action": action,
                    "symbol": params.get("symbol"),
                    "result": result
                }
                message = self.create_mcp_message("command_execution_result", response)
                self.send_message(self.central_agent, message)
            
            return result
        else:
            return {"status": "error", "message": f"不支持的CEX交易操作: {action}"}
    
    def _execute_dex_trade(self, action, params):
        """执行去中心化交易所交易"""
        if action == "approve":
            # 构建授权参数
            approve_params = {
                "token": params.get("token"),
                "spender": params.get("spender"),
                "amount": params.get("amount", "115792089237316195423570985008687907853269984665640564039457584007913129639935")  # max uint256
            }
            
            # 调用钱包代理进行授权
            message = self.create_mcp_message("approve_token", approve_params)
            result = self.send_message(self.wallet_agent, message)
        elif action == "swap":
            # 构建交易参数
            tx_params = {
                "to": params.get("router"),  # DEX路由合约地址
                "value": params.get("value", "0"),  # 如果使用原生代币作为输入，则设置value
                "data": params.get("data", "0x"),  # 合约调用数据
                "gas_price": params.get("gas_price"),
                "gas_limit": params.get("gas_limit")
            }
            
            # 调用钱包代理提交交易
            message = self.create_mcp_message("submit_transaction", tx_params)
            result = self.send_message(self.wallet_agent, message)
        else:
            return {"status": "error", "message": f"不支持的DEX交易操作: {action}"}
        
        # 回报结果给中央代理
        if self.central_agent and result.get("status") == "success":
            response = {
                "operation": "dex_trade",
                "action": action,
                "result": result
            }
            message = self.create_mcp_message("command_execution_result", response)
            self.send_message(self.central_agent, message)
        
        return result 