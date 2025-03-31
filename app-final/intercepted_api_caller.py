from api_caller import api_caller
from agent_interceptor import interceptor
import json
import time
import os

def intercepted_api_caller(api_type, endpoint, api_key, params, agent_name=None):
    """
    拦截API调用的函数，记录API调用并转发到原始API调用函数

    参数:
    api_type (str): API类型 (如 "etherscan", "opensea" 等)
    endpoint (str): API端点
    api_key (str): API密钥
    params (dict): API参数
    agent_name (str, 可选): 调用API的代理名称

    返回:
    dict: 从API调用返回的数据
    """
    # 如果没有指定代理名称，使用默认名称
    if agent_name is None:
        agent_name = "UnknownAgent"

    # 记录API调用
    interceptor.intercept_api_call(agent_name, api_type, endpoint, params)

    # 调用原始API函数
    response_data = api_caller(api_type, endpoint, api_key, params)

    # 记录API响应
    interceptor.intercept_api_response(agent_name, api_type, response_data)

    # 特别处理LLM API调用，确保记录到llm.txt
    if api_type.upper() == "LLM":
        try:
            # 获取请求和响应内容
            prompt = params.get("prompt", "")
            if isinstance(params, str):
                prompt = params  # 如果params本身是字符串，直接使用
            
            content = ""
            if isinstance(response_data, dict) and "choices" in response_data:
                # 新版OpenAI API格式
                content = response_data["choices"][0]["message"]["content"]
            elif isinstance(response_data, str):
                # 字符串响应
                content = response_data
            else:
                # 尝试转换响应为字符串
                content = str(response_data)
            
            # 构建日志条目
            llm_log_entry = {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "agent": agent_name,
                "model": "gpt-3.5-turbo",  # 默认模型，如果有实际值应该替换
                "prompt": prompt,
                "response": content
            }
            
            # 确保日志记录到llm.txt
            with open("llm.txt", "a", encoding="utf-8") as f:
                f.write(json.dumps(llm_log_entry, ensure_ascii=False) + "\n")
            
            print(f"✅ LLM调用已记录到llm.txt: agent={agent_name}, prompt长度={len(prompt)}")
        except Exception as e:
            print(f"❌ 记录LLM调用到llm.txt失败: {str(e)}")

    return response_data 