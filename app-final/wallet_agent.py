from base_agent import BaseAgent

class WalletAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="WalletAgent")
        self.central_agent = None
        self.active_wallet = None
    
    def set_central_agent(self, agent):
        """设置Central Agent"""
        self.central_agent = agent
    
    def receive_message(self, message):
        """接收消息"""
        if message["type"] == "set_wallet":
            return self.set_wallet(message["content"])
        elif message["type"] == "submit_transaction":
            return self.submit_transaction(message["content"])
        elif message["type"] == "approve_token":
            return self.approve_token(message["content"])
        elif message["type"] == "get_balance":
            return self.get_balance(message["content"])
        return {"status": "error", "message": "未支持的消息类型"}
    
    def process(self, data=None):
        """处理任务"""
        if not data:
            return {"status": "error", "message": "未提供数据"}
        
        if "type" in data:
            if data["type"] == "set_wallet":
                return self.set_wallet(data.get("params", {}))
            elif data["type"] == "submit_transaction":
                return self.submit_transaction(data.get("params", {}))
            elif data["type"] == "approve_token":
                return self.approve_token(data.get("params", {}))
            elif data["type"] == "get_balance":
                return self.get_balance(data.get("params", {}))
        
        return {"status": "error", "message": "未支持的任务类型"}
    
    def set_wallet(self, params):
        """设置活动钱包"""
        if "address" not in params:
            return {"status": "error", "message": "缺少钱包地址"}
        
        address = params["address"]
        private_key = params.get("private_key", None)
        
        # 注意：实际应用中，应该谨慎处理私钥，这里仅为示例
        self.active_wallet = {
            "address": address,
            "private_key": private_key
        }
        
        return {
            "status": "success",
            "message": f"已设置活动钱包: {address}",
            "address": address
        }
    
    def submit_transaction(self, params):
        """提交交易"""
        if not self.active_wallet:
            return {"status": "error", "message": "未设置活动钱包"}
        
        if "to" not in params or "value" not in params:
            return {"status": "error", "message": "缺少必要的交易参数"}
        
        to_address = params["to"]
        value = params["value"]
        gas_price = params.get("gas_price", None)
        gas_limit = params.get("gas_limit", None)
        data = params.get("data", "0x")
        
        # 模拟交易构建和提交过程
        # 实际应用中，应该使用web3库与区块链交互
        try:
            # 这里仅打印交易信息，实际应该发送到区块链
            tx_info = {
                "from": self.active_wallet["address"],
                "to": to_address,
                "value": value,
                "gas_price": gas_price,
                "gas_limit": gas_limit,
                "data": data
            }
            
            print(f"模拟交易提交: {tx_info}")
            
            # 模拟交易哈希
            tx_hash = "0x" + "0" * 64
            
            # 回报执行结果给中央代理
            if self.central_agent:
                response = {
                    "transaction_type": "transfer",
                    "status": "success",
                    "tx_hash": tx_hash,
                    "from": self.active_wallet["address"],
                    "to": to_address,
                    "value": value
                }
                message = self.create_mcp_message("command_execution_result", response)
                self.send_message(self.central_agent, message)
            
            return {
                "status": "success",
                "message": "交易已提交",
                "tx_hash": tx_hash
            }
        except Exception as e:
            return {"status": "error", "message": f"交易提交失败: {str(e)}"}
    
    def approve_token(self, params):
        """批准代币授权"""
        if not self.active_wallet:
            return {"status": "error", "message": "未设置活动钱包"}
        
        if "token" not in params or "spender" not in params or "amount" not in params:
            return {"status": "error", "message": "缺少必要的授权参数"}
        
        token_address = params["token"]
        spender_address = params["spender"]
        amount = params["amount"]
        
        # 模拟授权交易构建和提交过程
        try:
            # 构建ERC20 approve函数调用数据
            # 实际应该使用web3库构建
            function_signature = "approve(address,uint256)"
            data = f"模拟approve函数调用数据 - {function_signature}"
            
            tx_info = {
                "from": self.active_wallet["address"],
                "to": token_address,
                "value": 0,
                "data": data,
                "parameters": {
                    "spender": spender_address,
                    "amount": amount
                }
            }
            
            print(f"模拟授权交易: {tx_info}")
            
            # 模拟交易哈希
            tx_hash = "0x" + "a" * 64
            
            # 回报执行结果给中央代理
            if self.central_agent:
                response = {
                    "transaction_type": "approve",
                    "status": "success",
                    "tx_hash": tx_hash,
                    "token": token_address,
                    "owner": self.active_wallet["address"],
                    "spender": spender_address,
                    "amount": amount
                }
                message = self.create_mcp_message("command_execution_result", response)
                self.send_message(self.central_agent, message)
            
            return {
                "status": "success",
                "message": "授权交易已提交",
                "tx_hash": tx_hash
            }
        except Exception as e:
            return {"status": "error", "message": f"授权交易提交失败: {str(e)}"}
    
    def get_balance(self, params):
        """获取钱包余额"""
        address = params.get("address", self.active_wallet["address"] if self.active_wallet else None)
        token = params.get("token", "ETH")  # 默认查询ETH余额
        
        if not address:
            return {"status": "error", "message": "未指定钱包地址"}
        
        # 模拟查询余额过程
        try:
            # 这里应该调用区块链API查询真实余额
            if token == "ETH":
                # 构建查询参数
                query_params = {
                    "module": "account",
                    "action": "balance",
                    "address": address,
                    "tag": "latest"
                }
                
                # 调用区块链API
                balance_result = self.api_caller.call_blockchain_api("balance", query_params)
                
                # 解析结果
                if "result" in balance_result:
                    balance = int(balance_result["result"]) / 1e18  # 转换为ETH单位
                else:
                    balance = 0
            else:
                # 代币余额查询
                query_params = {
                    "module": "account",
                    "action": "tokenbalance",
                    "contractaddress": token,
                    "address": address,
                    "tag": "latest"
                }
                
                # 调用区块链API
                balance_result = self.api_caller.call_blockchain_api("tokenbalance", query_params)
                
                # 解析结果
                if "result" in balance_result:
                    balance = int(balance_result["result"]) / 1e18  # 假设代币精度为18
                else:
                    balance = 0
            
            return {
                "status": "success",
                "address": address,
                "token": token,
                "balance": balance
            }
        except Exception as e:
            return {"status": "error", "message": f"获取余额失败: {str(e)}"} 