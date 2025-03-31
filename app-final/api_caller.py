import os
import time
import json
import requests
from openai import OpenAI
import sqlite3
import traceback

class APICaller:
    def __init__(self):
        self.config = self._load_config()
        self._setup_clients()
    
    def _load_config(self):
        """加载配置文件"""
        config = {}
        try:
            with open("config.txt", "r") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        try:
                            # 拆分行到等号，只取第一个等号
                            key_value = line.split("=", 1)
                            if len(key_value) == 2:
                                key, value = key_value
                                # 移除值中的注释部分
                                if "#" in value:
                                    value = value.split("#")[0]
                                # 去除前后空格和引号
                                config[key.strip()] = value.strip().strip('"').strip("'")
                        except ValueError:
                            continue
        except Exception as e:
            print(f"❌ 加载配置文件失败: {str(e)}")
        return config
    
    def _setup_clients(self):
        """设置API客户端"""
        try:
            # 使用新版OpenAI客户端
            api_key = self.config.get("API_KEY")
            base_url = self.config.get("BASE_URL")
            if not api_key:
                print("⚠️ 警告: 未配置API_KEY，API调用可能会失败")
            if not base_url:
                print("⚠️ 警告: 未配置BASE_URL，将使用默认URL")
            
            self.openai_client = OpenAI(
                api_key=api_key,
                base_url=base_url
            )
            print(f"✅ OpenAI客户端初始化成功: URL={base_url}")
        except Exception as e:
            print(f"❌ OpenAI客户端初始化失败: {str(e)}")
            # 继续执行，以便其他功能仍然可用
    
    def _log_api_call(self, api_type, request, response):
        """记录API调用"""
        if self.config.get("DEBUG_MODE") == "True":
            try:
                log_entry = {
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "api_type": api_type,
                    "request": request,
                    "response": response
                }
                
                # 确保response可序列化为JSON
                try:
                    json.dumps(log_entry)
                except TypeError:
                    # 如果不可序列化，则转换为字符串
                    log_entry["response"] = str(response)
                
                with open("logs.txt", "a", encoding="utf-8") as f:
                    f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
                
                if api_type.startswith("ERROR"):
                    print(f"❌ API错误 ({api_type}): {str(response)}")
            except Exception as e:
                print(f"❌ 记录API调用失败: {str(e)}")
    
    def call_llm_api(self, prompt):
        """调用LLM API"""
        try:
            if self.config.get("DEBUG_MODE") == "True":
                print(f"🔄 调用LLM API: prompt长度={len(prompt)} 字符")
            
            # 使用新版API调用方式
            response = self.openai_client.chat.completions.create(
                model=self.config.get("MODEL"),
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            content = response.choices[0].message.content
            
            if self.config.get("DEBUG_MODE") == "True":
                print(f"✅ LLM API调用成功: 响应长度={len(content)} 字符")
            
            # 记录到logs.txt (只在DEBUG_MODE=True时)
            if self.config.get("DEBUG_MODE") == "True":
                self._log_api_call("LLM", prompt, content)
            
            # 专门记录到llm.txt (无论DEBUG_MODE如何)
            try:
                llm_log_entry = {
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "model": self.config.get("MODEL", "unknown"),
                    "prompt": prompt,
                    "response": content
                }
                with open("llm.txt", "a", encoding="utf-8") as f:
                    f.write(json.dumps(llm_log_entry, ensure_ascii=False) + "\n")
                print(f"📝 LLM API调用已记录到llm.txt: prompt长度={len(prompt)}, 响应长度={len(content)}")
            except Exception as e:
                print(f"❌ 记录LLM调用到llm.txt失败: {str(e)}")
                
            return content
        except Exception as e:
            error_detail = traceback.format_exc()
            error_msg = f"LLM API调用失败: {str(e)}\n{error_detail}"
            
            # 错误记录到logs.txt (只在DEBUG_MODE=True时)
            if self.config.get("DEBUG_MODE") == "True":
                self._log_api_call("LLM_ERROR", prompt, error_msg)
            
            # 记录错误到llm.txt (无论DEBUG_MODE如何)
            try:
                llm_error_entry = {
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "model": self.config.get("MODEL", "unknown"),
                    "prompt": prompt,
                    "error": error_msg
                }
                with open("llm.txt", "a", encoding="utf-8") as f:
                    f.write(json.dumps(llm_error_entry, ensure_ascii=False) + "\n")
                print(f"📝 LLM API调用错误已记录到llm.txt")
            except Exception as log_e:
                print(f"❌ 记录LLM错误到llm.txt失败: {str(log_e)}")
            
            # 构造一个模拟响应，确保即使API调用失败，系统仍能继续运行
            mock_response = f"<o>由于API调用错误，无法获取响应: {str(e)}</o>"
            return mock_response
    
    def call_blockchain_api(self, endpoint, params):
        """调用区块链API"""
        try:
            if self.config.get("DEBUG_MODE") == "True":
                print(f"🔄 调用区块链API: endpoint={endpoint}")
                
            url = self.config.get("BLOCKCHAIN_API_BASE")
            api_key = self.config.get("BLOCKCHAIN_API_KEY")
            
            if not url:
                error_msg = "未配置区块链API基础URL"
                self._log_api_call("BLOCKCHAIN_ERROR", {"endpoint": endpoint, "params": params}, error_msg)
                return {"error": error_msg}
            
            if not api_key or api_key == "YOUR_ETHERSCAN_API_KEY":
                if self.config.get("DEBUG_MODE") == "True":
                    print("⚠️ 使用模拟数据: 未配置有效的区块链API密钥")
                return {"result": "Error! Invalid API Key"}
            
            params["apikey"] = api_key
            
            response = requests.get(url, params=params)
            data = response.json()
            
            self._log_api_call("BLOCKCHAIN", {"endpoint": endpoint, "params": params}, data)
            return data
        except Exception as e:
            error_detail = traceback.format_exc()
            error_msg = f"区块链API调用失败: {str(e)}\n{error_detail}"
            self._log_api_call("BLOCKCHAIN_ERROR", {"endpoint": endpoint, "params": params}, error_msg)
            return {"error": error_msg}
    
    def call_exchange_api(self, exchange, endpoint, params, method="GET"):
        """调用交易所API"""
        try:
            if self.config.get("DEBUG_MODE") == "True":
                print(f"🔄 调用交易所API: exchange={exchange}, endpoint={endpoint}")
                
            if exchange.lower() == "binance":
                # 这里可以添加更多交易所的支持
                api_key = self.config.get("BINANCE_API_KEY")
                api_secret = self.config.get("BINANCE_API_SECRET")
                
                if not api_key or api_key == "YOUR_BINANCE_API_KEY":
                    if self.config.get("DEBUG_MODE") == "True":
                        print("⚠️ 使用模拟数据: 未配置有效的Binance API密钥")
                    return {"error": "Invalid API Key"}
                
                # 简化版的实现，实际应用中需要添加签名等验证
                headers = {"X-MBX-APIKEY": api_key}
                base_url = "https://api.binance.com"
                url = f"{base_url}{endpoint}"
                
                if method.upper() == "GET":
                    response = requests.get(url, headers=headers, params=params)
                else:
                    response = requests.post(url, headers=headers, data=params)
                
                data = response.json()
                self._log_api_call("EXCHANGE", {"exchange": exchange, "endpoint": endpoint, "params": params}, data)
                return data
            else:
                error_msg = f"不支持的交易所: {exchange}"
                self._log_api_call("EXCHANGE_ERROR", {"exchange": exchange, "endpoint": endpoint, "params": params}, error_msg)
                return {"error": error_msg}
        except Exception as e:
            error_detail = traceback.format_exc()
            error_msg = f"交易所API调用失败: {str(e)}\n{error_detail}"
            self._log_api_call("EXCHANGE_ERROR", {"exchange": exchange, "endpoint": endpoint, "params": params}, error_msg)
            return {"error": error_msg}
    
    def execute_sql(self, query, params=None):
        """执行SQL查询"""
        try:
            if self.config.get("DEBUG_MODE") == "True":
                print(f"🔄 执行SQL: query={query[:50]}..." if len(query) > 50 else f"🔄 执行SQL: query={query}")
                
            # 确保数据库文件目录存在
            db_file = "blockchain_data.db"
            dir_name = os.path.dirname(db_file)
            if dir_name and not os.path.exists(dir_name):
                os.makedirs(dir_name)
            
            conn = sqlite3.connect(db_file)
            cursor = conn.cursor()
            
            if params:
                result = cursor.execute(query, params)
            else:
                result = cursor.execute(query)
                
            if query.strip().upper().startswith(("SELECT", "PRAGMA")):
                data = result.fetchall()
                columns = [description[0] for description in cursor.description] if cursor.description else []
                conn.close()
                
                # 将结果转换为字典列表
                rows = []
                for row in data:
                    rows.append(dict(zip(columns, row)))
                
                if self.config.get("DEBUG_MODE") == "True":
                    print(f"✅ SQL查询成功: 返回 {len(rows)} 行结果")
                
                self._log_api_call("SQL", query, {"rows": len(rows), "sample": rows[:3] if rows else []})
                return rows
            else:
                conn.commit()
                affected = cursor.rowcount
                conn.close()
                
                if self.config.get("DEBUG_MODE") == "True":
                    print(f"✅ SQL执行成功: 影响 {affected} 行")
                
                self._log_api_call("SQL", query, {"affected_rows": affected})
                return {"affected_rows": affected}
        except Exception as e:
            error_detail = traceback.format_exc()
            error_msg = f"SQL执行失败: {str(e)}\n{error_detail}"
            self._log_api_call("SQL_ERROR", query, error_msg)
            
            if self.config.get("DEBUG_MODE") == "True":
                print(f"❌ SQL执行失败: {str(e)}")
                
            return {"error": error_msg}

# 创建APICaller类的单例实例
_api_caller_instance = APICaller()

# 提供api_caller函数，供其他模块导入使用
def api_caller(api_type, endpoint, api_key, params):
    """
    外部可调用的API接口函数
    
    参数:
    api_type (str): API类型 (如 "etherscan", "opensea", "LLM" 等)
    endpoint (str): API端点
    api_key (str): API密钥
    params (dict/str): API参数或提示内容
    
    返回:
    dict/str: API调用的响应
    """
    if api_type.upper() == "LLM":
        # 对于LLM调用，假设params包含提示信息或直接是提示字符串
        prompt = params
        if isinstance(params, dict) and "prompt" in params:
            prompt = params["prompt"]
        
        print(f"🔄 通过api_caller函数调用LLM API: prompt长度={len(prompt) if isinstance(prompt, str) else '未知'}")
        
        # 调用实例的方法
        result = _api_caller_instance.call_llm_api(prompt)
        
        # 直接在这里也记录到llm.txt，确保被记录
        try:
            llm_log_entry = {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "call_path": "api_caller_function",
                "model": _api_caller_instance.config.get("MODEL", "unknown"),
                "prompt": prompt,
                "response": result
            }
            with open("llm.txt", "a", encoding="utf-8") as f:
                f.write(json.dumps(llm_log_entry, ensure_ascii=False) + "\n")
            print(f"📝 (api_caller函数) LLM API调用已直接记录到llm.txt")
        except Exception as e:
            print(f"❌ (api_caller函数) 记录LLM调用到llm.txt失败: {str(e)}")
        
        return result
    
    elif api_type.upper() == "BLOCKCHAIN":
        return _api_caller_instance.call_blockchain_api(endpoint, params)
    
    elif api_type.upper().startswith("EXCHANGE"):
        exchange = api_type.split("_")[1] if "_" in api_type else "binance"
        return _api_caller_instance.call_exchange_api(exchange, endpoint, params)
    
    elif api_type.upper() == "SQL":
        return _api_caller_instance.execute_sql(endpoint, params)
    
    else:
        error_msg = f"不支持的API类型: {api_type}"
        print(f"❌ {error_msg}")
        return {"error": error_msg} 