from api_caller import api_caller
from agent_interceptor import interceptor

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

    return response_data
