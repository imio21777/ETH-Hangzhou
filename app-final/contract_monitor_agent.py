from base_agent import BaseAgent
import json

class ContractMonitorAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="ContractMonitorAgent")
        self.data_clean_agent = None
        self.latest_info = {}
        self.monitored_contracts = []  # 监控的合约地址列表
    
    def set_data_clean_agent(self, agent):
        """设置DataClean Agent"""
        self.data_clean_agent = agent
    
    def add_monitored_contract(self, contract_address, label=None):
        """添加要监控的合约"""
        contract_info = {
            "address": contract_address,
            "label": label or "未命名合约"
        }
        if contract_info not in self.monitored_contracts:
            self.monitored_contracts.append(contract_info)
            self.log_action("添加监控合约", f"{contract_address} ({label})")
    
    def remove_monitored_contract(self, contract_address):
        """移除监控的合约"""
        for i, contract in enumerate(self.monitored_contracts):
            if contract["address"] == contract_address:
                self.monitored_contracts.pop(i)
                self.log_action("移除监控合约", contract_address)
                return True
        return False
    
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
            elif message["type"] == "add_contract":
                if "address" in message["content"]:
                    self.add_monitored_contract(
                        message["content"]["address"],
                        message["content"].get("label")
                    )
                return {"status": "success", "message": "合约已添加到监控列表"}
            elif message["type"] == "remove_contract":
                if "address" in message["content"]:
                    result = self.remove_monitored_contract(message["content"]["address"])
                    if result:
                        return {"status": "success", "message": "合约已从监控列表移除"}
                    else:
                        return {"status": "error", "message": "未找到该合约"}
            elif message["type"] == "request_contract_analysis":
                return self.analyze_contract_activity(message["content"])
            
            return {"status": "error", "message": "未支持的消息类型"}
        except Exception as e:
            self.log_action("错误", f"处理消息失败: {str(e)}")
            return {"status": "error", "message": f"处理消息失败: {str(e)}"}
    
    def process_info_update(self, info):
        """处理更新的信息"""
        try:
            self.log_action("处理更新的信息")
            self.latest_info = info
            
            # 处理市场信息中的合约相关数据
            contract_data = self._extract_contract_data(info)
            
            # 如果有DataClean Agent，将处理后的数据发送给它
            if self.data_clean_agent:
                message = self.create_mcp_message("processed_data", {
                    "type": "contract_activities",
                    "data": contract_data
                })
                self.send_message(self.data_clean_agent, message)
            
            return {"status": "success", "message": "合约活动信息已处理"}
        except Exception as e:
            self.log_action("错误", f"处理信息更新失败: {str(e)}")
            return {"status": "error", "message": f"处理信息更新失败: {str(e)}"}
    
    def process(self, data=None):
        """处理任务"""
        if not data:
            return {"status": "error", "message": "未提供数据"}
        
        if "type" in data and data["type"] == "analyze_contract":
            return self.analyze_contract_activity(data.get("params", {}))
        
        return {"status": "error", "message": "未支持的任务类型"}
    
    def analyze_contract_activity(self, params):
        """分析合约活动"""
        self.log_action("分析合约活动")
        if not self.latest_info:
            return {"status": "error", "message": "没有最新的市场信息"}
        
        contract_address = params.get("address", None)
        
        # 如果没有指定合约地址，但有监控列表，则使用监控列表中的第一个
        if not contract_address and self.monitored_contracts:
            contract_address = self.monitored_contracts[0]["address"]
        
        if not contract_address:
            return {"status": "error", "message": "未指定合约地址且监控列表为空"}
        
        # 从最新信息中提取合约相关数据
        contract_activity = self.latest_info.get("contract_activity", {})
        
        # 检查是否有该合约的交互记录
        contract_interactions = []
        if "contract_activity" in contract_activity:
            result = contract_activity["contract_activity"].get("result", [])
            for tx in result:
                if tx.get("to", "").lower() == contract_address.lower():
                    contract_interactions.append(tx)
        
        if not contract_interactions:
            return {"status": "warning", "message": f"没有找到合约 {contract_address} 的最近交互"}
        
        # 使用LLM分析合约活动
        # 提取前5条交互
        sample_interactions = contract_interactions[:5]
        
        analysis_prompt = f"""
        分析以下智能合约 {contract_address} 的活动数据:
        
        合约交互: {sample_interactions}
        
        请回答以下问题:
        1. 这个合约可能是什么类型的协议（例如DEX、借贷协议、NFT市场等）？
        2. 最近的交互显示了什么样的活动模式？
        3. 合约的活动量是增加还是减少？
        4. 是否存在任何可能的安全风险或异常活动？
        
        请返回你的分析结果，格式为<o>分析结果</o>
        """
        
        analysis_result = self.call_llm(analysis_prompt)
        extracted_analysis = self.extract_output(analysis_result)
        
        return {
            "status": "success", 
            "contract": contract_address,
            "analysis": extracted_analysis
        }
    
    def _extract_contract_data(self, info):
        """从市场信息中提取合约相关数据"""
        self.log_action("提取合约相关数据")
        contract_data = {
            "timestamp": info.get("timestamp", 0),
            "contracts": []
        }
        
        try:
            # 获取合约活动数据
            contract_activity = info.get("contract_activity", {})
            if isinstance(contract_activity, str):
                self.log_action("警告", f"合约活动为字符串: {contract_activity[:100]}...")
                try:
                    contract_activity = json.loads(contract_activity)
                except Exception as e:
                    self.log_action("错误", f"合约活动JSON解析失败: {str(e)}")
                    contract_activity = {}
            
            # 处理监控列表中的合约
            for contract in self.monitored_contracts:
                contract_address = contract["address"]
                contract_label = contract["label"]
                
                # 查找该合约的交互
                interactions = []
                if "contract_activity" in contract_activity:
                    contract_act_data = contract_activity["contract_activity"]
                    if isinstance(contract_act_data, str):
                        self.log_action("警告", f"合约活动数据为字符串: {contract_act_data[:100]}...")
                        try:
                            contract_act_data = json.loads(contract_act_data)
                        except Exception as e:
                            self.log_action("错误", f"合约活动数据JSON解析失败: {str(e)}")
                            contract_act_data = {}
                    
                    result = contract_act_data.get("result", [])
                    if isinstance(result, str):
                        self.log_action("警告", f"合约活动结果为字符串: {result[:100]}...")
                        try:
                            result = json.loads(result)
                        except Exception as e:
                            self.log_action("错误", f"合约活动结果JSON解析失败: {str(e)}")
                            result = []
                    
                    # 确保结果是列表
                    if not isinstance(result, list):
                        self.log_action("警告", f"合约活动结果不是列表，而是 {type(result)}")
                        result = []
                    
                    for tx in result:
                        if not isinstance(tx, dict):
                            self.log_action("警告", f"合约交易不是字典，而是 {type(tx)}")
                            continue
                        
                        if tx.get("to", "").lower() == contract_address.lower():
                            interactions.append(tx)
                
                self.log_action("获取合约交互", f"合约 {contract_address} 有 {len(interactions)} 条交互")
                
                # 查询合约代币信息
                token_supply = None
                if "token_supply" in contract_activity and contract_activity["token_supply"].get("result", ""):
                    token_contract = contract_activity.get("token_supply", {}).get("contractaddress", "")
                    if token_contract.lower() == contract_address.lower():
                        token_supply = contract_activity["token_supply"].get("result", "")
                
                # 使用LLM分析合约类型
                contract_type = "未知"
                if interactions:
                    prompt = f"""
                    根据以下智能合约交互，判断这可能是什么类型的合约:
                    
                    合约地址: {contract_address}
                    交互记录: {interactions[:3]}
                    
                    请从以下选项中选择最可能的一种，或提供自己的分类：
                    1. DEX (去中心化交易所)
                    2. 借贷协议
                    3. NFT市场
                    4. 稳定币合约
                    5. 流动性挖矿
                    6. 跨链桥
                    7. DAO治理
                    8. 其他(请说明)
                    
                    请只返回合约类型，格式为<o>合约类型</o>
                    """
                    
                    result = self.call_llm(prompt)
                    contract_type = self.extract_output(result)
                
                # 添加到合约数据
                contract_data["contracts"].append({
                    "address": contract_address,
                    "label": contract_label,
                    "type": contract_type,
                    "interactions": interactions[:10],  # 最多保存10条交互记录
                    "token_supply": token_supply
                })
        except Exception as e:
            self.log_action("错误", f"提取合约数据失败: {str(e)}")
        
        return contract_data 