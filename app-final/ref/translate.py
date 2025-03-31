import requests
import json
import os
import time

# 从配置文件加载API信息
def load_config():
    config = {}
    try:
        with open("config.txt", "r") as f:
            for line in f:
                if "=" in line:
                    key, value = line.strip().split("=", 1)
                    config[key.strip()] = value.strip().strip('"\'')
        return config
    except Exception as e:
        print(f"加载配置文件时出错: {str(e)}")
        return {
            "BASE_URL": "https://api2.aigcbest.top/v1",
            "API_KEY": "sk-NiMvTTja0AQMrEkNgOElafUVP6HnOcrBu0tJhfTeucBSJzU3",
            "MODEL": "gpt-4o-2024-11-20"
        }

# 获取延时时间
def get_delay_time():
    """从配置中获取延时时间"""
    config = load_config()
    try:
        delay_time = float(config.get('DELAY_TIME', '0'))
        return delay_time
    except (ValueError, TypeError):
        return 0.0

# 翻译文本为中文
def translate_to_chinese(text):
    """
    使用大模型API将文本翻译为中文

    Args:
        text: 需要翻译的文本

    Returns:
        翻译后的中文文本
    """
    if not text:
        return text

    config = load_config()
    base_url = config.get("BASE_URL", "https://api2.aigcbest.top/v1")
    api_key = config.get("API_KEY", "")
    model = config.get("MODEL", "gpt-4o-2024-11-20")

    endpoint = f"{base_url}/chat/completions"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    # 准备请求数据
    data = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": "你是一个专业的翻译助手，负责将区块链和加密货币相关的英文内容精准翻译成中文。保持专业术语的准确性，同时确保翻译结果通俗易懂。"
            },
            {
                "role": "user",
                "content": f"请将以下文本翻译成中文，保持专业术语的准确性：\n\n{text}"
            }
        ],
        "temperature": 0.3
    }

    try:
        response = requests.post(
            endpoint,
            headers=headers,
            json=data,
            timeout=30
        )

        response.raise_for_status()
        result = response.json()

        # 添加翻译请求后的延时
        delay_time = get_delay_time()
        if delay_time > 0:
            print(f"翻译请求延时: {delay_time}秒")
            time.sleep(delay_time)

        if "choices" in result and len(result["choices"]) > 0:
            translated_text = result["choices"][0]["message"]["content"]
            return translated_text
        else:
            print(f"翻译API返回了意外的响应格式: {json.dumps(result)}")
            return text

    except Exception as e:
        print(f"翻译API调用出错: {str(e)}")
        return text

# 翻译JSON响应
def translate_response(response_data):
    """
    翻译API响应中的内容

    Args:
        response_data: API响应的JSON数据

    Returns:
        翻译后的响应数据
    """
    if isinstance(response_data, dict):
        # 检查是否有嵌套的内容需要翻译
        translated_data = {}
        for key, value in response_data.items():
            if key == "content" and isinstance(value, str):
                # 翻译内容字段
                translated_data[key] = translate_to_chinese(value)
            elif key == "result" and isinstance(value, dict):
                # 递归翻译结果字段
                translated_data[key] = translate_response(value)
            elif isinstance(value, (dict, list)):
                # 递归翻译嵌套的字典或列表
                translated_data[key] = translate_response(value)
            else:
                # 保持其他字段不变
                translated_data[key] = value
        return translated_data
    elif isinstance(response_data, list):
        # 处理列表类型的数据
        return [translate_response(item) for item in response_data]
    else:
        # 其他类型的数据保持不变
        return response_data

# 示例用法
if __name__ == "__main__":
    # 测试翻译功能
    test_text = "The transaction shows a large whale moving funds from a known exchange to a new wallet address."
    result = translate_to_chinese(test_text)
    print(f"原文: {test_text}")
    print(f"翻译: {result}")
