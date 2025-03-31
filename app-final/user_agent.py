from base_agent import BaseAgent
import json
import traceback

class UserAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="UserAgent")
        self.central_agent = None
    
    def set_central_agent(self, agent):
        """设置Central Agent"""
        self.central_agent = agent
    
    def receive_message(self, message):
        """接收消息"""
        if message["type"] == "system_response":
            return self.process_system_response(message["content"])
        return {"status": "error", "message": "未支持的消息类型"}
    
    def process_user_request(self, user_query):
        """处理用户请求"""
        # 使用LLM解析用户自然语言请求
        try:
            structured_request = self._parse_user_query(user_query)
            
            if not structured_request:
                return {"status": "error", "message": "无法解析用户请求"}
            
            # 如果有中央代理，将请求转发给它
            if self.central_agent:
                message = self.create_mcp_message("user_request", structured_request)
                result = self.send_message(self.central_agent, message)
                
                # 处理结果
                return self._format_response(result, user_query)
            
            return {"status": "error", "message": "未连接到中央代理"}
        except Exception as e:
            error_detail = traceback.format_exc()
            print(f"处理用户请求时发生错误: {str(e)}\n{error_detail}")
            return {"status": "error", "message": f"处理请求时发生错误: {str(e)}"}
    
    def process_system_response(self, response):
        """处理系统响应"""
        # 这里可以对系统响应做一些处理
        return {"status": "success", "response": response}
    
    def process(self, data=None):
        """处理任务"""
        if not data:
            return {"status": "error", "message": "未提供数据"}
        
        if "type" in data and data["type"] == "user_query":
            return self.process_user_request(data["query"])
        
        return {"status": "error", "message": "未支持的任务类型"}
    
    def _parse_user_query(self, user_query):
        """解析用户查询为结构化请求"""
        # 使用LLM理解用户意图
        understanding_prompt = f"""
        请分析以下用户请求，理解用户的意图，并将其转换为系统可以理解的结构化格式。
        你只需要识别请求类型和提取参数，不需要判断请求是否可以执行。
        
        用户请求:
        {user_query}
        
        请识别以下信息:
        1. 请求类型: 用户想要执行什么操作? (例如:market_analysis, coin_info, whale_analysis, contract_analysis, transaction_analysis, set_alarm, trade_operation, sql_query等)
        2. 关键参数: 请求中包含的重要参数(如币种、地址、数量、金额等)
        
        即使请求可能无法执行(如购买比特币)，也要正确分类为trade_operation，不要自行判断是否可行。
        
        请以JSON格式返回，格式为<o>
        {{
            "request_type": "操作类型",
            "parameters": {{
                "参数1": "值1",
                "参数2": "值2"
            }},
            "additional_info": "附加信息"
        }}
        </o>
        """
        
        try:
            result = self.call_llm(understanding_prompt)
            structured_json = self.extract_output(result)
            
            # 尝试解析JSON
            structured_request = json.loads(structured_json)
            
            # 添加原始查询
            structured_request["original_query"] = user_query
            return structured_request
        except json.JSONDecodeError as e:
            print(f"JSON解析错误: {e}, 原始返回: {structured_json}")
            # 如果JSON解析失败，则返回简单结构
            return {
                "request_type": "unknown",
                "parameters": {
                    "raw_query": user_query
                },
                "additional_info": f"解析失败，原始输出: {structured_json[:100]}...",
                "original_query": user_query
            }
        except Exception as e:
            print(f"解析用户查询时发生未知错误: {str(e)}")
            return {
                "request_type": "unknown",
                "parameters": {
                    "raw_query": user_query
                },
                "additional_info": "",
                "original_query": user_query
            }
    
    def _format_response(self, result, original_query):
        """格式化响应"""
        try:
            # 使用LLM生成自然语言响应
            format_prompt = f"""
            请将以下系统响应转换为自然语言回复:
            
            用户原始查询: {original_query}
            系统响应: {result}
            
            请生成一个友好、信息丰富的回复，格式为<o>回复内容</o>
            """
            
            llm_response = self.call_llm(format_prompt)
            formatted_response = self.extract_output(llm_response)
            
            return {
                "status": "success",
                "original_result": result,
                "formatted_response": formatted_response
            }
        except Exception as e:
            error_detail = traceback.format_exc()
            print(f"格式化响应时发生错误: {str(e)}\n{error_detail}")
            return {
                "status": "error", 
                "message": f"格式化响应时发生错误: {str(e)}",
                "original_result": result
            } 