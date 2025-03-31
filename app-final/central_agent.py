from base_agent import BaseAgent
import json
import time
import traceback

class CentralAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="CentralAgent")
        # 初始化其他代理的引用
        self.info_process_agent = None
        self.data_clean_agent = None
        self.cex_withdraw_agent = None
        self.specific_coin_whale_agent = None
        self.freq_tx_agent = None
        self.contract_monitor_agent = None
        self.basic_coin_info_agent = None
        self.wallet_agent = None
        self.cex_agent = None
        self.auto_trade_agent = None
        self.alarm_agent = None
    
    def register_agents(self, agents_dict):
        """注册其他代理"""
        for key, agent in agents_dict.items():
            if key == "info_process_agent":
                self.info_process_agent = agent
            elif key == "data_clean_agent":
                self.data_clean_agent = agent
            elif key == "cex_withdraw_agent":
                self.cex_withdraw_agent = agent
            elif key == "specific_coin_whale_agent":
                self.specific_coin_whale_agent = agent
            elif key == "freq_tx_agent":
                self.freq_tx_agent = agent
            elif key == "contract_monitor_agent":
                self.contract_monitor_agent = agent
            elif key == "basic_coin_info_agent":
                self.basic_coin_info_agent = agent
            elif key == "wallet_agent":
                self.wallet_agent = agent
            elif key == "cex_agent":
                self.cex_agent = agent
            elif key == "auto_trade_agent":
                self.auto_trade_agent = agent
            elif key == "alarm_agent":
                self.alarm_agent = agent
    
    def receive_message(self, message):
        """接收消息"""
        if message["type"] == "user_request":
            return self.process_user_request(message["content"])
        elif message["type"] == "command_execution_result":
            return self.process_command_result(message["content"])
        return {"status": "error", "message": "未支持的消息类型"}
    
    def process_user_request(self, request):
        """处理用户请求"""
        try:
            # 首先更新市场信息
            if self.info_process_agent:
                update_message = self.create_mcp_message("request_info_update", {})
                update_result = self.send_message(self.info_process_agent, update_message)
                if update_result.get("status") != "success":
                    return {"status": "error", "message": "无法更新市场信息"}
            
            # 获取请求类型
            if isinstance(request, dict) and "request_type" in request:
                request_type = request["request_type"]
            else:
                # 使用LLM分析请求类型
                request_type = self._analyze_request_type(request)
            
            # 根据请求类型进行处理
            if request_type == "market_analysis":
                return self._handle_market_analysis_request(request)
            elif request_type == "coin_info":
                return self._handle_coin_info_request(request)
            elif request_type == "whale_analysis":
                return self._handle_whale_analysis_request(request)
            elif request_type == "contract_analysis":
                return self._handle_contract_analysis_request(request)
            elif request_type == "transaction_analysis":
                return self._handle_transaction_analysis_request(request)
            elif request_type == "set_alarm":
                return self._handle_set_alarm_request(request)
            elif request_type == "trade_operation":
                return self._handle_trade_operation_request(request)
            elif request_type == "sql_query":
                return self._handle_sql_query_request(request)
            else:
                return {"status": "error", "message": f"未知的请求类型: {request_type}"}
        except Exception as e:
            error_detail = traceback.format_exc()
            print(f"处理用户请求时发生错误: {str(e)}\n{error_detail}")
            return {"status": "error", "message": f"处理请求时发生错误: {str(e)}"}
    
    def process_command_result(self, result):
        """处理命令执行结果"""
        return {"status": "success", "message": "命令执行结果已处理", "result": result}
    
    def process(self, data=None):
        """处理任务"""
        if not data:
            return {"status": "error", "message": "未提供数据"}
        
        if "type" in data and data["type"] == "user_request":
            return self.process_user_request(data["request"])
        
        return {"status": "error", "message": "未支持的任务类型"}
    
    def _analyze_request_type(self, request):
        """分析用户请求类型"""
        # 如果request是字典并且已经包含request_type，直接返回
        if isinstance(request, dict) and "request_type" in request:
            return request["request_type"]
        
        # 确定要分析的文本
        request_text = request["original_query"] if isinstance(request, dict) and "original_query" in request else str(request)
        
        analysis_prompt = f"""
        请识别以下用户请求属于哪种类型:
        
        {request_text}
        
        请从以下选项中选择一种:
        1. market_analysis - 市场分析请求
        2. coin_info - 币种信息请求
        3. whale_analysis - 鲸鱼活动分析请求
        4. contract_analysis - 合约分析请求
        5. transaction_analysis - 交易分析请求
        6. set_alarm - 设置警报请求
        7. trade_operation - 交易操作请求 (包括任何购买、出售、转账、提款币种的请求)
        8. sql_query - SQL查询请求
        9. other - 其他请求
        
        注意：所有涉及"购买"、"卖出"、"出售"、"交易"、"转账"、"提款"等操作的请求，都应该归类为"trade_operation"。
        
        请只返回对应的类型代码，格式为<o>类型代码</o>
        """
        
        result = self.call_llm(analysis_prompt)
        request_type = self.extract_output(result)
        
        return request_type
    
    def _handle_market_analysis_request(self, request):
        """处理市场分析请求"""
        if self.basic_coin_info_agent:
            message = self.create_mcp_message("request_market_analysis", {})
            result = self.send_message(self.basic_coin_info_agent, message)
            return result
        return {"status": "error", "message": "无法执行市场分析"}
    
    def _handle_coin_info_request(self, request):
        """处理币种信息请求"""
        # 如果参数中已有币种信息，直接使用
        if isinstance(request, dict) and "parameters" in request and "coin" in request["parameters"]:
            coin_symbol = request["parameters"]["coin"]
        else:
            # 使用LLM提取请求中的币种
            request_text = request["original_query"] if isinstance(request, dict) and "original_query" in request else str(request)
            extract_prompt = f"""
            请从以下请求中提取用户想要了解的币种符号:
            
            {request_text}
            
            请只返回币种符号(如BTC, ETH, USDT等)，格式为<o>币种符号</o>
            """
            
            result = self.call_llm(extract_prompt)
            coin_symbol = self.extract_output(result)
        
        if self.basic_coin_info_agent:
            message = self.create_mcp_message("get_coin_info", {
                "coin": coin_symbol
            })
            result = self.send_message(self.basic_coin_info_agent, message)
            return result
        return {"status": "error", "message": "无法获取币种信息"}
    
    def _handle_whale_analysis_request(self, request):
        """处理鲸鱼活动分析请求"""
        # 如果参数中已有币种信息，直接使用
        if isinstance(request, dict) and "parameters" in request and "coin" in request["parameters"]:
            coin_symbol = request["parameters"]["coin"]
        else:
            # 使用LLM提取请求中的币种
            request_text = request["original_query"] if isinstance(request, dict) and "original_query" in request else str(request)
            extract_prompt = f"""
            请从以下请求中提取用户想要分析的币种符号:
            
            {request_text}
            
            请只返回币种符号(如BTC, ETH, USDT等)，如果没有提到具体币种，则返回ETH，格式为<o>币种符号</o>
            """
            
            result = self.call_llm(extract_prompt)
            coin_symbol = self.extract_output(result)
        
        if self.specific_coin_whale_agent:
            message = self.create_mcp_message("request_whale_analysis", {
                "coin": coin_symbol
            })
            result = self.send_message(self.specific_coin_whale_agent, message)
            return result
        return {"status": "error", "message": "无法分析鲸鱼活动"}
    
    def _handle_contract_analysis_request(self, request):
        """处理合约分析请求"""
        # 如果参数中已有合约地址，直接使用
        if isinstance(request, dict) and "parameters" in request and "address" in request["parameters"]:
            contract_address = request["parameters"]["address"]
        else:
            # 使用LLM提取请求中的合约地址
            request_text = request["original_query"] if isinstance(request, dict) and "original_query" in request else str(request)
            extract_prompt = f"""
            请从以下请求中提取用户想要分析的智能合约地址:
            
            {request_text}
            
            请只返回合约地址(0x开头的地址)，格式为<o>合约地址</o>
            """
            
            result = self.call_llm(extract_prompt)
            contract_address = self.extract_output(result)
        
        if self.contract_monitor_agent:
            message = self.create_mcp_message("request_contract_analysis", {
                "address": contract_address
            })
            result = self.send_message(self.contract_monitor_agent, message)
            return result
        return {"status": "error", "message": "无法分析合约活动"}
    
    def _handle_transaction_analysis_request(self, request):
        """处理交易分析请求"""
        # 如果参数中已有分析类型，直接使用
        if isinstance(request, dict) and "parameters" in request and "analysis_type" in request["parameters"]:
            analysis_type = request["parameters"]["analysis_type"]
        else:
            # 确定是高频交易分析还是交易所提款分析
            request_text = request["original_query"] if isinstance(request, dict) and "original_query" in request else str(request)
            determine_prompt = f"""
            请从以下请求中判断用户是想分析高频交易地址还是交易所提款情况:
            
            {request_text}
            
            请返回 "high_freq" 或 "cex_withdrawal"，格式为<o>分析类型</o>
            """
            
            result = self.call_llm(determine_prompt)
            analysis_type = self.extract_output(result)
        
        if analysis_type == "high_freq":
            # 分析高频交易
            if self.freq_tx_agent:
                address = None
                # 如果参数中已有地址，直接使用
                if isinstance(request, dict) and "parameters" in request and "address" in request["parameters"]:
                    address = request["parameters"]["address"]
                else:
                    # 尝试提取特定地址
                    request_text = request["original_query"] if isinstance(request, dict) and "original_query" in request else str(request)
                    extract_prompt = f"""
                    请从以下请求中提取用户想要分析的具体地址(如果有):
                    
                    {request_text}
                    
                    如果请求中包含具体地址，请返回该地址，否则返回"all"，格式为<o>地址或all</o>
                    """
                    
                    result = self.call_llm(extract_prompt)
                    address = self.extract_output(result)
                
                params = {}
                if address and address != "all":
                    params["address"] = address
                
                message = self.create_mcp_message("request_freq_analysis", params)
                result = self.send_message(self.freq_tx_agent, message)
                return result
        else:
            # 分析交易所提款
            if self.cex_withdraw_agent:
                message = self.create_mcp_message("request_analysis", {})
                result = self.send_message(self.cex_withdraw_agent, message)
                return result
        
        return {"status": "error", "message": "无法分析交易活动"}
    
    def _handle_set_alarm_request(self, request):
        """处理设置警报请求"""
        # 如果有Alarm Agent实现，可以在这里添加逻辑
        if self.alarm_agent:
            # 从请求中提取警报参数
            if isinstance(request, dict) and "parameters" in request:
                params = request["parameters"]
            else:
                # 使用默认参数
                params = {
                    "id": f"alarm_{int(time.time())}",
                    "description": "用户设置的警报",
                    "condition": "SELECT * FROM whale_transactions WHERE value > 10000 LIMIT 1"
                }
            
            message = self.create_mcp_message("set_alarm", params)
            result = self.send_message(self.alarm_agent, message)
            return result
        return {"status": "error", "message": "警报功能尚未实现"}
    
    def _handle_trade_operation_request(self, request):
        """处理交易操作请求"""
        if self.auto_trade_agent:
            # 从请求中提取交易参数
            if isinstance(request, dict) and "parameters" in request:
                params = request["parameters"]
                
                # 确定交易目标和操作
                if "target" not in params:
                    params["target"] = "cex"  # 默认使用中心化交易所
                
                if "action" not in params:
                    params["action"] = "buy"  # 默认执行买入操作
                
                message = self.create_mcp_message("execute_trade", params)
                result = self.send_message(self.auto_trade_agent, message)
                return result
            else:
                return {"status": "error", "message": "缺少交易参数"}
        return {"status": "error", "message": "交易功能尚未实现"}
    
    def _handle_sql_query_request(self, request):
        """处理SQL查询请求"""
        # 如果参数中已有SQL查询，直接使用
        if isinstance(request, dict) and "parameters" in request and "sql" in request["parameters"]:
            sql_query = request["parameters"]["sql"]
        else:
            # 使用LLM从请求中提取SQL查询
            request_text = request["original_query"] if isinstance(request, dict) and "original_query" in request else str(request)
            extract_prompt = f"""
            请从以下请求中提取或生成SQL查询语句:
            
            {request_text}
            
            请返回完整的SQL查询语句，格式为<sql>SQL查询语句</sql>
            """
            
            result = self.call_llm(extract_prompt)
            
            # 提取SQL查询
            sql_query = self.extract_output(result, tag="sql")
        
        if not sql_query:
            return {"status": "error", "message": "无法提取或生成SQL查询"}
        
        if self.data_clean_agent:
            message = self.create_mcp_message("sql_query", {
                "query": sql_query
            })
            result = self.send_message(self.data_clean_agent, message)
            
            # 使用LLM解释SQL查询结果
            if result.get("status") == "success":
                explanation_prompt = f"""
                请解释以下SQL查询的结果:
                
                SQL查询: {sql_query}
                查询结果: {result.get("result", [])}
                
                请提供简洁明了的解释，格式为<o>解释</o>
                """
                
                explanation_result = self.call_llm(explanation_prompt)
                explanation = self.extract_output(explanation_result)
                
                result["explanation"] = explanation
            
            return result
        
        return {"status": "error", "message": "无法执行SQL查询"} 