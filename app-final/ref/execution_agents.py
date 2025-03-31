from typing import Dict, Any, List
import json
import random
from datetime import datetime, timedelta
from base_agent import BaseAgent
from api_caller import api_caller
import time

class AutoTradeAgent(BaseAgent):
    def __init__(self, name: str = "AutoTradeAgent", llm_model: str = None):
        super().__init__(name, llm_model)
        self.connected_agents = {}

    def register_agent(self, agent_name: str, agent_instance: BaseAgent):
        """Register execution agents to receive trade orders"""
        self.connected_agents[agent_name] = agent_instance
        print(f"Agent {agent_name} registered with {self.name}")

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process trading action request and route to appropriate execution agent.

        Args:
            input_data: Dictionary containing trade parameters

        Returns:
            Execution result
        """
        action = input_data.get("action", "")

        if action == "execute_trade":
            return self._execute_trade(input_data.get("parameters", {}))
        else:
            return {
                "status": "error",
                "message": f"Unknown action: {action}"
            }

    def _execute_trade(self, trade_params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a trade using the appropriate agent"""
        # Validate parameters
        if not trade_params:
            return {
                "status": "error",
                "message": "No trade parameters provided"
            }

        # Log the trade request
        if self.interceptor:
            self.interceptor.intercept_message(
                self.name,
                "System",
                f"Trade request received: {json.dumps(trade_params)}",
                "trade_request"
            )

        # Determine which agent should handle the trade
        venue = trade_params.get("venue", "").lower()

        if venue in ["wallet", "web3", "metamask", "hardwallet"]:
            agent_name = "WalletAgent"
        else:
            agent_name = "CEXAgent"

        # Check if the agent is available
        if agent_name not in self.connected_agents:
            return {
                "status": "error",
                "message": f"{agent_name} not available for trade execution"
            }

        # Route the trade to the appropriate agent
        agent = self.connected_agents[agent_name]
        result = agent.process({
            "action": "execute_trade",
            "parameters": trade_params
        })

        # Log the result
        if self.interceptor:
            self.interceptor.intercept_message(
                self.name,
                agent_name,
                f"Trade result: {json.dumps(result)}",
                "trade_result"
            )

        return {
            "status": result.get("status", "error"),
            "message": result.get("message", "Unknown error"),
            "executed_by": agent_name,
            "execution_details": result.get("details", {})
        }

class AlarmAgent(BaseAgent):
    def __init__(self, name: str = "AlarmAgent", llm_model: str = None):
        super().__init__(name, llm_model)
        self.alerts = []

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process alert requests and send notifications.

        Args:
            input_data: Dictionary containing alert parameters

        Returns:
            Alert processing result
        """
        action = input_data.get("action", "")

        if action == "setup_alert":
            return self._setup_alert(input_data.get("parameters", {}))
        elif action == "send_alert":
            return self._send_alert(input_data.get("alert_data", {}))
        else:
            return {
                "status": "error",
                "message": f"Unknown action: {action}"
            }

    def _setup_alert(self, alert_params: Dict[str, Any]) -> Dict[str, Any]:
        """Set up an alert based on specified parameters"""
        # Validate parameters
        if not alert_params:
            return {
                "status": "error",
                "message": "No alert parameters provided"
            }

        token = alert_params.get("token", "")
        condition = alert_params.get("condition", "")
        threshold = alert_params.get("threshold", "")
        notification_method = alert_params.get("notification_method", "telegram")

        if not (token and condition):
            return {
                "status": "error",
                "message": "Missing required alert parameters"
            }

        # In a real implementation, store the alert in a database
        # For this demo, we'll just return a successful setup response
        alert_id = f"alert_{int(time.time())}"

        return {
            "status": "success",
            "message": f"Alert set up successfully for {token}",
            "alert_id": alert_id,
            "parameters": alert_params
        }

    def _send_alert(self, alert_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send an alert notification"""
        # Validate the alert data
        if not alert_data:
            return {
                "status": "error",
                "message": "No alert data provided"
            }

        # Determine notification method (default to Telegram)
        notification_method = alert_data.get("notification_method", "telegram")

        # Format the alert message
        alert_type = alert_data.get("type", "general")
        content = alert_data.get("content", "")
        if alert_type == "insight_alert":
            source = alert_data.get("source", "Unknown")
            message = f"🚨 ALERT: {source}\n{content}"
        elif alert_type == "recommendation_alert":
            action = alert_data.get("action", "")
            message = f"⚠️ RECOMMENDED ACTION: {action}"
        else:
            message = f"ℹ️ NOTIFICATION: {content}"

        # Send notification via the appropriate channel
        if notification_method == "telegram":
            result = self._send_telegram_notification(message)
        else:
            result = {"status": "error", "message": f"Unsupported notification method: {notification_method}"}

        return {
            "status": result.get("status", "error"),
            "message": result.get("message", ""),
            "notification_method": notification_method
        }

    def _send_telegram_notification(self, message: str) -> Dict[str, Any]:
        """Send notification via Telegram"""
        # Get Telegram configuration
        bot_token = self.config.get("TELEGRAM_BOT_TOKEN", "")
        chat_id = self.config.get("TELEGRAM_CHAT_ID", "")

        if not (bot_token and chat_id):
            return {
                "status": "error",
                "message": "Missing Telegram configuration"
            }

        # Prepare API call
        endpoint = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        params = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "Markdown"
        }

        # Send message
        result = api_caller(
            "telegram",
            endpoint,
            bot_token,
            params,
            self.name
        )

        if result.get("ok", False):
            return {
                "status": "success",
                "message": "Notification sent via Telegram"
            }
        else:
            return {
                "status": "error",
                "message": f"Failed to send Telegram notification: {result.get('description', 'Unknown error')}"
            }

class WalletAgent(BaseAgent):
    def __init__(self, name: str = "WalletAgent", llm_model: str = None):
        super().__init__(name, llm_model)

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process wallet transaction requests.

        Args:
            input_data: Dictionary containing transaction parameters

        Returns:
            Transaction result
        """
        action = input_data.get("action", "")

        if action == "execute_trade":
            return self._execute_wallet_transaction(input_data.get("parameters", {}))
        elif action == "get_balance":
            return self._get_wallet_balance(input_data.get("parameters", {}))
        else:
            return {
                "status": "error",
                "message": f"Unknown action: {action}"
            }

    def _execute_wallet_transaction(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a blockchain transaction using wallet"""
        # Validate parameters
        if not params:
            return {
                "status": "error",
                "message": "No transaction parameters provided"
            }

        action_type = params.get("action_type", "").lower()
        token = params.get("token", "").upper()
        amount = params.get("amount", "")
        price = params.get("price", "market")

        if not (action_type and token and amount):
            return {
                "status": "error",
                "message": "Missing required transaction parameters"
            }

        # Determine if this is a token transaction or native coin (ETH, BNB, etc.)
        is_token = token not in ["ETH", "BNB", "MATIC", "AVAX"]

        # Prepare blockchain transaction parameters
        if action_type == "buy":
            if is_token:
                # Token swap transaction
                tx_params = {
                    "method": "tokenSwap",
                    "fromToken": "ETH",  # Assuming ETH as base currency
                    "toToken": token,
                    "amount": amount,
                    "slippage": "1.0"  # 1% slippage
                }
            else:
                return {
                    "status": "error",
                    "message": f"Cannot buy native token {token} directly. Please use an exchange."
                }
        elif action_type == "sell":
            if is_token:
                # Token swap transaction
                tx_params = {
                    "method": "tokenSwap",
                    "fromToken": token,
                    "toToken": "ETH",  # Assuming ETH as base currency
                    "amount": amount,
                    "slippage": "1.0"  # 1% slippage
                }
            else:
                # Simple ETH transfer
                tx_params = {
                    "method": "sendTransaction",
                    "to": "0x...",  # Target address would be specified in real implementation
                    "value": amount,
                    "data": ""
                }
        else:
            return {
                "status": "error",
                "message": f"Unsupported action type: {action_type}"
            }

        # Execute blockchain transaction
        result = api_caller(
            "blockchain",
            endpoint=f"{self.config.get('BLOCKCHAIN_API_URL', '')}/transaction",
            api_key=self.config.get('BLOCKCHAIN_API_KEY', ''),
            params=tx_params,
            agent_name=self.name
        )

        # Format and return result
        if "hash" in result:
            return {
                "status": "success",
                "message": f"Transaction executed: {action_type} {amount} {token}",
                "details": {
                    "tx_hash": result.get("hash", ""),
                    "block_number": result.get("blockNumber", ""),
                    "gas_used": result.get("gasUsed", ""),
                    "status": "Pending"  # Actual status would be checked in real implementation
                }
            }
        else:
            return {
                "status": "error",
                "message": f"Transaction failed: {result.get('message', 'Unknown error')}",
                "details": result
            }

    def _get_wallet_balance(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get wallet balance"""
        address = params.get("address", "")
        token = params.get("token", "").upper()

        if not address:
            return {
                "status": "error",
                "message": "No wallet address provided"
            }

        # Query blockchain for balance
        balance_params = {
            "method": "getBalance",
            "address": address,
            "token": token
        }

        result = api_caller(
            "blockchain",
            endpoint=f"{self.config.get('BLOCKCHAIN_API_URL', '')}/api",
            api_key=self.config.get('BLOCKCHAIN_API_KEY', ''),
            params=balance_params,
            agent_name=self.name
        )

        if "balance" in result:
            return {
                "status": "success",
                "balance": result.get("balance", "0"),
                "token": token or "ETH"
            }
        else:
            return {
                "status": "error",
                "message": f"Failed to get balance: {result.get('message', 'Unknown error')}"
            }

class CEXAgent(BaseAgent):
    def __init__(self, name: str = "CEXAgent", llm_model: str = None):
        super().__init__(name, llm_model)

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process CEX (Centralized Exchange) trading requests.

        Args:
            input_data: Dictionary containing trade parameters

        Returns:
            Trade execution result
        """
        action = input_data.get("action", "")

        if action == "execute_trade":
            return self._execute_cex_trade(input_data.get("parameters", {}))
        elif action == "get_balance":
            return self._get_cex_balance(input_data.get("parameters", {}))
        elif action == "get_ticker":
            return self._get_ticker_price(input_data.get("parameters", {}))
        else:
            return {
                "status": "error",
                "message": f"Unknown action: {action}"
            }

    def _execute_cex_trade(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a trade on a centralized exchange"""
        # Validate parameters
        if not params:
            return {
                "status": "error",
                "message": "No trade parameters provided"
            }

        action_type = params.get("action_type", "").lower()
        token = params.get("token", "").upper()
        amount = params.get("amount", "")
        price = params.get("price", "market")
        venue = params.get("venue", "binance").lower()

        if not (action_type and token and amount):
            return {
                "status": "error",
                "message": "Missing required trade parameters"
            }

        # Format the trading pair
        symbol = f"{token}USDT"  # Assuming USDT as the base currency

        # Determine order type
        order_type = "MARKET" if price == "market" else "LIMIT"

        # Prepare CEX API parameters
        cex_params = {
            "method": "place_order",
            "exchange": venue,
            "symbol": symbol,
            "side": action_type.upper(),
            "type": order_type,
            "quantity": amount
        }

        # Add price for limit orders
        if order_type == "LIMIT":
            cex_params["price"] = price

        # Determine which API keys to use based on the venue
        api_key = ""
        api_secret = ""
        if venue == "binance":
            api_key = self.config.get("BINANCE_API_KEY", "")
            api_secret = self.config.get("BINANCE_SECRET_KEY", "")
            cex_params["api_secret"] = api_secret  # Needed for authentication
        elif venue == "coinbase":
            api_key = self.config.get("COINBASE_API_KEY", "")
            api_secret = self.config.get("COINBASE_SECRET_KEY", "")
            cex_params["api_secret"] = api_secret  # Needed for authentication

        if not api_key:
            return {
                "status": "error",
                "message": f"No API key found for {venue}"
            }

        # Execute the CEX trade
        result = api_caller(
            "cex",
            endpoint=f"{venue}/api/v3/order",  # Generic endpoint format
            api_key=api_key,
            params=cex_params,
            agent_name=self.name
        )

        # Format and return result
        if result.get("status") == "success":
            return {
                "status": "success",
                "message": f"Trade executed on {venue}: {action_type} {amount} {token}",
                "details": {
                    "order_id": result.get("data", {}).get("order_id", ""),
                    "symbol": result.get("data", {}).get("symbol", ""),
                    "type": result.get("data", {}).get("type", ""),
                    "side": result.get("data", {}).get("side", ""),
                    "price": result.get("data", {}).get("price", ""),
                    "quantity": result.get("data", {}).get("quantity", ""),
                    "status": result.get("data", {}).get("status", "")
                }
            }
        else:
            return {
                "status": "error",
                "message": f"Trade failed: {result.get('message', 'Unknown error')}",
                "details": result
            }

    def _get_cex_balance(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get account balance on a centralized exchange"""
        venue = params.get("venue", "binance").lower()

        # Determine which API keys to use based on the venue
        api_key = ""
        api_secret = ""
        if venue == "binance":
            api_key = self.config.get("BINANCE_API_KEY", "")
            api_secret = self.config.get("BINANCE_SECRET_KEY", "")
        elif venue == "coinbase":
            api_key = self.config.get("COINBASE_API_KEY", "")
            api_secret = self.config.get("COINBASE_SECRET_KEY", "")

        if not api_key:
            return {
                "status": "error",
                "message": f"No API key found for {venue}"
            }

        # Prepare CEX API parameters
        cex_params = {
            "method": "account_balance",
            "exchange": venue,
            "api_secret": api_secret  # Needed for authentication
        }

        # Get account balance
        result = api_caller(
            "cex",
            endpoint=f"{venue}/api/v3/account",  # Generic endpoint format
            api_key=api_key,
            params=cex_params,
            agent_name=self.name
        )

        # Format and return result
        if result.get("status") == "success":
            return {
                "status": "success",
                "balances": result.get("data", {}).get("balances", {}),
                "venue": venue
            }
        else:
            return {
                "status": "error",
                "message": f"Failed to get balance: {result.get('message', 'Unknown error')}"
            }

    def _get_ticker_price(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get current price for a trading pair"""
        token = params.get("token", "").upper()
        venue = params.get("venue", "binance").lower()

        if not token:
            return {
                "status": "error",
                "message": "No token specified"
            }

        # Format the trading pair
        symbol = f"{token}USDT"  # Assuming USDT as the base currency

        # Prepare CEX API parameters
        cex_params = {
            "method": "ticker_price",
            "exchange": venue,
            "symbol": symbol
        }

        # No authentication needed for public endpoints like ticker price

        # Get ticker price
        result = api_caller(
            "cex",
            endpoint=f"{venue}/api/v3/ticker/price",  # Generic endpoint format
            api_key="",  # Public endpoint, no API key needed
            params=cex_params,
            agent_name=self.name
        )

        # Format and return result
        if result.get("status") == "success":
            return {
                "status": "success",
                "symbol": symbol,
                "price": result.get("data", {}).get("price", ""),
                "venue": venue
            }
        else:
            return {
                "status": "error",
                "message": f"Failed to get price: {result.get('message', 'Unknown error')}"
            }
