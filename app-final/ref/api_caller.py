import json
import random
import string
import requests
import os
import time
from typing import Dict, Any, Optional
from datetime import datetime

def _load_config() -> Dict[str, str]:
    """Load configuration from config.txt file"""
    config = {}
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.txt')

    if os.path.exists(config_path):
        try:
            with open(config_path, 'r') as file:
                for line in file:
                    line = line.strip()
                    # Skip comments and empty lines
                    if not line or line.startswith('#'):
                        continue

                    # Parse key-value pairs
                    if '=' in line:
                        key, value = line.split('=', 1)
                        config[key.strip()] = value.strip().strip('"\'')
        except Exception as e:
            print(f"Error loading config: {e}")
    else:
        print(f"Config file not found at {config_path}")

    return config

# Load configuration once
_CONFIG = _load_config()

# 获取延时时间
def _get_delay_time() -> float:
    """从配置中获取延时时间"""
    try:
        delay_time = float(_CONFIG.get('DELAY_TIME', '0'))
        return delay_time
    except (ValueError, TypeError):
        return 0.0

def api_caller(api_type: str, endpoint: str, api_key: str, params: Dict[str, Any], agent_name: str = None) -> Dict[str, Any]:
    """
    API caller function that handles all API calls with a demo mode switch.

    Args:
        api_type: API type ('blockchain', 'llm_api', 'cex', 'telegram')
        endpoint: API endpoint
        api_key: API key (will be masked in logs)
        params: API call parameters
        agent_name: Name of the agent making the call

    Returns:
        API response data
    """
    # Mask API key for console output
    masked_key = api_key[:4] + '*' * (len(api_key) - 8) + api_key[-4:] if len(api_key) > 8 else '****'
    console_output = {
        "api_type": api_type,
        "endpoint": endpoint,
        "api_key": masked_key,
        "params": params
    }

    print(f"API CALL: {json.dumps(console_output, indent=2)}")

    # Try to import and use interceptor if available
    try:
        from agent_interceptor import interceptor
        if agent_name:
            interceptor.intercept_api_call(agent_name, api_type, endpoint, params)
    except ImportError:
        print("Interceptor not available, API call won't be recorded")

    # Check if demo mode is enabled
    demo_mode = _CONFIG.get('DEMO_MODE', 'True').lower() in ('true', 'yes', '1')

    # Process the API call based on type and demo mode
    result = None

    if api_type == "llm_api":
        # Always use real LLM API regardless of demo mode
        result = call_real_llm_api(endpoint, api_key, params)
    elif demo_mode:
        # Use mock data for other API types in demo mode
        if api_type == "blockchain":
            result = generate_blockchain_mock_data(params)
        elif api_type == "cex":
            result = generate_cex_mock_data(params)
        elif api_type == "telegram":
            result = generate_telegram_mock_data(params)
        else:
            result = {"status": "error", "message": f"Unknown API type: {api_type}"}
    else:
        # Use real API calls when not in demo mode
        if api_type == "blockchain":
            result = call_real_blockchain_api(endpoint, api_key, params)
        elif api_type == "cex":
            result = call_real_cex_api(endpoint, api_key, params)
        elif api_type == "telegram":
            result = call_real_telegram_api(endpoint, api_key, params)
        else:
            result = {"status": "error", "message": f"Unknown API type: {api_type}"}

    # Record API response if interceptor is available
    try:
        from agent_interceptor import interceptor
        if agent_name:
            interceptor.intercept_api_response(agent_name, api_type, result)
    except ImportError:
        pass
    
    # 添加延时
    delay_time = _get_delay_time()
    if delay_time > 0:
        print(f"API调用延时: {delay_time}秒")
        time.sleep(delay_time)

    return result

def call_real_llm_api(endpoint: str, api_key: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Call real LLM API

    Args:
        endpoint: API endpoint
        api_key: API key
        params: Request parameters

    Returns:
        API response
    """
    try:
        # Ensure proper handling of Chinese and Unicode characters
        headers = {
            "Content-Type": "application/json; charset=utf-8",
            "Authorization": f"Bearer {api_key}"
        }

        # Convert request parameters to JSON with proper Unicode handling
        request_body = json.dumps(params, ensure_ascii=False)

        # Debug output
        print(f"Sending request to: {endpoint}")

        response = requests.post(
            endpoint,
            headers=headers,
            data=request_body.encode('utf-8'),
            timeout=30
        )

        # Output response status
        print(f"API response status: {response.status_code}")

        # Check response status
        response.raise_for_status()

        # Parse response
        result = response.json()

        # Debug: print full API response
        print(f"API response: {json.dumps(result, ensure_ascii=False, indent=2)}")

        # 添加延时
        delay_time = _get_delay_time()
        if delay_time > 0:
            print(f"LLM API响应延时: {delay_time}秒")
            time.sleep(delay_time)

        # Format return result
        if "choices" in result and len(result["choices"]) > 0:
            # Extract content
            content = result["choices"][0]["message"]["content"]
            return {
                "content": content,
                "model": params.get("model", ""),
                "usage": result.get("usage", {})
            }
        else:
            # If response format doesn't match expectations, try to extract content
            print(f"Warning: Expected 'choices' field not found in API response")
            if "message" in result:
                # If there's an error message
                return {
                    "content": str(result.get("message", "")),
                    "model": params.get("model", ""),
                    "usage": {}
                }
            else:
                # Try to get any possible response content
                return {
                    "content": str(result),
                    "model": params.get("model", ""),
                    "usage": {}
                }
    except requests.exceptions.RequestException as e:
        print(f"LLM API request error: {str(e)}")
        # Use mock data as fallback on error
        return generate_llm_mock_data(params)
    except json.JSONDecodeError as e:
        print(f"LLM API response JSON parsing error: {str(e)}")
        print(f"Raw response: {response.text if 'response' in locals() else 'unavailable'}")
        # Response is not valid JSON
        return generate_llm_mock_data(params)
    except Exception as e:
        print(f"Unexpected error during LLM API call: {str(e)}")
        # Use mock data as fallback for any other error
        return generate_llm_mock_data(params)

def call_real_blockchain_api(endpoint: str, api_key: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Call real blockchain API (e.g., Etherscan, Infura)

    Args:
        endpoint: API endpoint
        api_key: API key
        params: Request parameters

    Returns:
        API response
    """
    try:
        # Add API key to parameters
        if "apikey" not in params:
            params["apikey"] = api_key

        # Make the API request
        response = requests.get(endpoint, params=params, timeout=30)
        response.raise_for_status()

        # Parse and return the response
        return response.json()
    except Exception as e:
        print(f"Blockchain API error: {str(e)}")
        # Return error object
        return {"status": "error", "message": f"Blockchain API error: {str(e)}"}

def call_real_cex_api(endpoint: str, api_key: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Call real centralized exchange API (e.g., Binance, Coinbase)

    Args:
        endpoint: API endpoint
        api_key: API key
        params: Request parameters

    Returns:
        API response
    """
    try:
        # Add authentication headers based on exchange type
        exchange = params.get("exchange", "").lower()
        headers = {}

        if exchange == "binance":
            headers = {
                "X-MBX-APIKEY": api_key
            }
            # Handle Binance signature if needed
            # ...
        elif exchange == "coinbase":
            # Handle Coinbase authentication
            # ...
            pass

        # Make the API request
        response = requests.get(endpoint, headers=headers, params=params, timeout=30)
        response.raise_for_status()

        # Parse and return the response
        return response.json()
    except Exception as e:
        print(f"CEX API error: {str(e)}")
        # Return error object
        return {"status": "error", "message": f"CEX API error: {str(e)}"}

def call_real_telegram_api(endpoint: str, api_key: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Call real Telegram API for alerts

    Args:
        endpoint: API endpoint
        api_key: API key (bot token)
        params: Request parameters

    Returns:
        API response
    """
    try:
        # Make the API request
        response = requests.post(endpoint, json=params, timeout=30)
        response.raise_for_status()

        # Parse and return the response
        return response.json()
    except Exception as e:
        print(f"Telegram API error: {str(e)}")
        # Return error object
        return {"status": "error", "message": f"Telegram API error: {str(e)}"}

def generate_blockchain_mock_data(params: Dict[str, Any]) -> Dict[str, Any]:
    """Generate mock blockchain data"""
    method = params.get("method", "")

    if method == "getTransaction":
        return {
            "hash": "0x" + ''.join(random.choices(string.hexdigits, k=64)).lower(),
            "from": "0x" + ''.join(random.choices(string.hexdigits, k=40)).lower(),
            "to": "0x" + ''.join(random.choices(string.hexdigits, k=40)).lower(),
            "value": str(random.randint(1, 10000000000000000000)),
            "gas": str(random.randint(21000, 300000)),
            "gasPrice": str(random.randint(1000000000, 50000000000)),
            "input": "0x" + ''.join(random.choices(string.hexdigits, k=random.randint(8, 200))).lower(),
            "blockNumber": str(random.randint(10000000, 15000000)),
            "blockHash": "0x" + ''.join(random.choices(string.hexdigits, k=64)).lower(),
            "timestamp": str(int(datetime.now().timestamp()))
        }
    elif method == "getBalance":
        return {
            "address": params.get("address", "0x" + ''.join(random.choices(string.hexdigits, k=40)).lower()),
            "balance": str(random.randint(1, 1000000000000000000000))
        }
    elif method == "getTokenInfo":
        return {
            "name": random.choice(["Ethereum", "Binance Coin", "Uniswap", "Chainlink", "Polygon", "Arbitrum"]),
            "symbol": random.choice(["ETH", "BNB", "UNI", "LINK", "MATIC", "ARB"]),
            "totalSupply": str(random.randint(1000000, 1000000000000)),
            "decimals": str(random.randint(6, 18))
        }
    else:
        return {"status": "success", "message": "Generic blockchain data"}

def generate_llm_mock_data(params: Dict[str, Any]) -> Dict[str, Any]:
    """Generate mock LLM API response data"""
    messages = params.get("messages", [])
    last_message = messages[-1]["content"] if messages else ""

    # Determine response type based on last message content
    if any(keyword in last_message.lower() for keyword in ["classify", "分类"]):
        # Classification request
        if any(keyword in last_message.lower() for keyword in ["transaction", "交易"]):
            categories = ["transaction_analysis", "market_alert", "trading_action", "unknown"]
            # Guess more likely classification based on input content
            if any(keyword in last_message.lower() for keyword in ["purchase", "buy", "sell", "trade", "购买", "买入", "卖出"]):
                mock_content = "trading_action"
            elif any(keyword in last_message.lower() for keyword in ["alert", "notify", "when", "警报", "提醒", "当"]):
                mock_content = "market_alert"
            elif any(keyword in last_message.lower() for keyword in ["analyse", "check", "transaction", "分析", "查看"]):
                mock_content = "transaction_analysis"
            else:
                mock_content = random.choice(categories)
        else:
            # Other classification requests
            mock_content = "classification_result"

    elif any(keyword in last_message.lower() for keyword in ["extract", "params", "parameters", "提取", "参数"]):
        # Parameter extraction request
        if any(keyword in last_message.lower() for keyword in ["trade", "trading", "交易"]):
            # Trading parameters
            mock_content = '{"action_type": "buy", "token": "BTC", "amount": "0.5", "price": "40000", "venue": "binance"}'
        elif any(keyword in last_message.lower() for keyword in ["alert", "notification", "警报", "提醒"]):
            # Alert parameters
            mock_content = '{"token": "ETH", "condition": "price above", "threshold": "2500", "notification_method": "email"}'
        elif any(keyword in last_message.lower() for keyword in ["hash", "transaction", "哈希", "交易"]):
            # Transaction hash extraction
            mock_content = "0x7d3c5142ef8063322ad0815155a6627365a5b0548f1b488588b54bf6a242a7c8"
        else:
            # Default parameter extraction
            mock_content = '{"param1": "value1", "param2": "value2"}'

    else:
        # Generic response
        mock_responses = [
            "I've analyzed the transaction data and found unusual whale activity.",
            "This appears to be a regular transfer from a known exchange.",
            "Contract interaction suggests potential arbitrage opportunity.",
            "Based on historical patterns, this wallet belongs to a known market maker.",
            "The transaction is flagged due to association with previously identified suspicious addresses.",
            "This wallet has been active recently, possibly an institutional investor.",
            "Large funds inflow detected for this token, may cause price volatility.",
            "Transaction pattern shows this is a regular DCA (Dollar Cost Averaging) purchase."
        ]
        mock_content = random.choice(mock_responses)

    return {
        "id": "chatcmpl-" + ''.join(random.choices(string.ascii_letters + string.digits, k=10)),
        "object": "chat.completion",
        "created": int(datetime.now().timestamp()),
        "model": params.get("model", "gpt-4"),
        "content": mock_content,
        "usage": {
            "prompt_tokens": len(last_message) // 4,
            "completion_tokens": len(mock_content) // 4,
            "total_tokens": (len(last_message) // 4) + (len(mock_content) // 4)
        }
    }

def generate_cex_mock_data(params: Dict[str, Any]) -> Dict[str, Any]:
    """Generate mock cryptocurrency exchange API data"""
    method = params.get("method", "")

    if method == "account_balance":
        # Generate mock account balance data
        coins = ["BTC", "ETH", "BNB", "XRP", "ADA", "SOL", "DOT", "DOGE", "AVAX", "MATIC"]
        balances = {}

        for coin in coins:
            if random.random() > 0.5:  # Only include some coins
                balances[coin] = {
                    "free": round(random.uniform(0, 10), 8),
                    "locked": round(random.uniform(0, 1), 8),
                    "total": 0  # Will be calculated below
                }
                balances[coin]["total"] = round(balances[coin]["free"] + balances[coin]["locked"], 8)

        return {
            "status": "success",
            "data": {
                "balances": balances
            }
        }

    elif method == "place_order":
        # Generate mock order placement response
        order_types = ["LIMIT", "MARKET"]
        sides = ["BUY", "SELL"]

        return {
            "status": "success",
            "data": {
                "order_id": ''.join(random.choices(string.digits, k=10)),
                "symbol": params.get("symbol", "BTCUSDT"),
                "side": params.get("side", random.choice(sides)),
                "type": params.get("type", random.choice(order_types)),
                "price": params.get("price", str(round(random.uniform(20000, 50000), 2))),
                "quantity": params.get("quantity", str(round(random.uniform(0.1, 2), 6))),
                "time": int(datetime.now().timestamp() * 1000),
                "status": "FILLED" if random.random() > 0.8 else "NEW"
            }
        }

    elif method == "ticker_price":
        # Generate mock ticker price data
        base_prices = {
            "BTC": 40000,
            "ETH": 2500,
            "BNB": 350,
            "XRP": 0.5,
            "ADA": 0.3,
            "SOL": 100,
            "DOT": 5,
            "DOGE": 0.1,
            "AVAX": 25,
            "MATIC": 0.6
        }

        symbol = params.get("symbol", "BTCUSDT")
        coin = symbol[:3] if len(symbol) >= 3 else "BTC"
        base_price = base_prices.get(coin, 100)

        # Add some randomness to price
        price = base_price * (1 + random.uniform(-0.05, 0.05))

        return {
            "status": "success",
            "data": {
                "symbol": symbol,
                "price": str(round(price, 2)),
                "timestamp": int(datetime.now().timestamp() * 1000)
            }
        }

    else:
        return {
            "status": "success",
            "data": {
                "message": "Mock CEX API response",
                "timestamp": int(datetime.now().timestamp())
            }
        }

def generate_telegram_mock_data(params: Dict[str, Any]) -> Dict[str, Any]:
    """Generate mock Telegram API response data"""
    return {
        "ok": True,
        "result": {
            "message_id": random.randint(1000, 9999),
            "chat": {
                "id": params.get("chat_id", "123456789"),
                "type": "private"
            },
            "date": int(datetime.now().timestamp()),
            "text": params.get("text", "Mock message"),
            "entities": []
        }
    }
