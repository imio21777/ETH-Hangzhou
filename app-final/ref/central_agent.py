from typing import Dict, Any, List, Optional
import json
from base_agent import BaseAgent
from agent_interceptor import interceptor

class CentralAgent(BaseAgent):
    def __init__(self, name: str = "CentralAgent", llm_model: str = None):
        super().__init__(name, llm_model)
        self.connected_agents = {}

    def register_agent(self, agent_name: str, agent_instance: BaseAgent):
        """Register an agent with the central coordinator"""
        self.connected_agents[agent_name] = agent_instance
        # Record agent registration event
        interceptor.intercept_message(self.name, agent_name, f"Agent {agent_name} registered with {self.name}", "registration")

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process user input and coordinate with other agents.

        Args:
            input_data: User input data

        Returns:
            Processed response and action recommendations
        """
        # Record input request
        interceptor.intercept_message("User", self.name, f"Received request: {json.dumps(input_data)}", "user_request")

        # Determine the type of request from user input
        request_type = self._determine_request_type(input_data)

        # Record request type determination
        interceptor.intercept_message(self.name, "System", f"Request type determined: {request_type}", "processing")

        # Process based on request type
        if request_type == "transaction_analysis":
            result = self._process_transaction_analysis(input_data)

        elif request_type == "market_alert":
            result = self._process_market_alert(input_data)

        elif request_type == "trading_action":
            result = self._process_trading_action(input_data)

        elif request_type == "data_query":
            result = self._process_data_query(input_data)

        else:
            # Default response for unknown request types
            result = {
                "response_type": "unknown_request",
                "message": "I'm not sure how to process this request. Please provide more specific information."
            }

        # Record processing result
        interceptor.intercept_message(self.name, "User", f"Processing complete: {json.dumps(result)}", "response")

        return result

    def _determine_request_type(self, input_data: Dict[str, Any]) -> str:
        """Determine the type of request from user input"""
        # Use LLM to classify the user request
        user_message = input_data.get("user_message", "")

        if not user_message:
            # If there's a tx_hash, assume it's a transaction analysis
            if "tx_hash" in input_data:
                return "transaction_analysis"
            return "unknown"

        # Simple keyword detection for quick classification as fallback
        user_message_lower = user_message.lower()

        # Trading-related keywords (in English and Chinese)
        trading_keywords = ['buy', 'sell', 'trade', 'limit', 'market', 'order', 'purchase',
                           '购买', '买入', '卖出', '交易', '下单', '限价', '市价']

        # Alert-related keywords (in English and Chinese)
        alert_keywords = ['alert', 'notification', 'notify', 'when', 'if', 'reaches', 'drops', 'falls',
                         '提醒', '警报', '通知', '当', '如果', '达到', '超过', '下跌']

        # Transaction analysis keywords (in English and Chinese)
        analysis_keywords = ['analyze', 'analysis', 'transaction', 'tx', 'hash', 'check',
                            '分析', '交易', '哈希', '查看', '0x']

        # Data query keywords (in English and Chinese)
        query_keywords = ['query', 'find', 'search', 'show me', 'list', 'whales', 'transactions', 'database',
                         '查询', '搜索', '找到', '显示', '列出', '大户', '交易记录', '数据库']

        # Simple classification based on keywords
        if any(keyword in user_message_lower for keyword in trading_keywords):
            simple_classification = "trading_action"
        elif any(keyword in user_message_lower for keyword in alert_keywords):
            simple_classification = "market_alert"
        elif any(keyword in user_message_lower for keyword in analysis_keywords):
            simple_classification = "transaction_analysis"
        elif any(keyword in user_message_lower for keyword in query_keywords):
            simple_classification = "data_query"
        else:
            simple_classification = "unknown"

        # Try to use LLM for more accurate classification
        try:
            prompt = f"""
            Classify the following user request into one of these categories:
            1. transaction_analysis - User wants information about a specific transaction
            2. market_alert - User wants to set up alerts for market conditions
            3. trading_action - User wants to execute a trade or set up automated trading
            4. data_query - User wants to search or query the database for information
            5. unknown - The request doesn't fit into the above categories

            User request: "{user_message}"

            Return just the category name (e.g., "transaction_analysis").
            """

            system_prompt = "You are a blockchain request classifier. Return only the category name."

            response = self.call_llm(prompt, system_prompt)
            llm_classification = response.strip().lower().replace('"', '')

            # Validate LLM classification
            if llm_classification in ["transaction_analysis", "market_alert", "trading_action", "data_query", "unknown"]:
                return llm_classification
            else:
                print(f"LLM returned unexpected classification: {llm_classification}, using keyword classification instead")
                return simple_classification

        except Exception as e:
            print(f"LLM classification failed: {str(e)}, using keyword classification instead")
            return simple_classification

    def _process_transaction_analysis(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a transaction analysis request"""
        # Check if we have the necessary agents
        required_agents = ["InfoProcessAgent", "DataCleanAgent"]
        for agent_name in required_agents:
            if agent_name not in self.connected_agents:
                return {
                    "error": f"Missing required agent: {agent_name}",
                    "success": False
                }

        # Get transaction data
        tx_hash = input_data.get("tx_hash", "")
        if not tx_hash:
            if "user_message" in input_data:
                # Try to extract tx hash from user message
                tx_hash = self._extract_tx_hash(input_data["user_message"])

            if not tx_hash:
                return {
                    "error": "No transaction hash provided",
                    "success": False
                }

        # Process through InfoProcessAgent
        info_process_agent = self.connected_agents["InfoProcessAgent"]
        result = info_process_agent.process({"tx_hash": tx_hash})

        # Data Clean Agent processes the combined data from all agents
        data_clean_agent = self.connected_agents["DataCleanAgent"]
        clean_data = data_clean_agent.process(result)

        # Determine if any alerts should be triggered
        alerts = self._check_for_alerts(clean_data)

        # Determine if any trading actions should be taken
        trading_actions = self._check_for_trading_actions(clean_data)

        # Prepare final response
        response = {
            "response_type": "transaction_analysis",
            "analysis": clean_data,
            "alerts": alerts,
            "trading_actions": trading_actions,
            "success": True
        }

        return response

    def _process_market_alert(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a market alert setup request"""
        user_message = input_data.get("user_message", "")

        # Use LLM to extract alert parameters
        prompt = f"""
        Extract market alert parameters from the following user request:

        User request: "{user_message}"

        Extract the following information:
        1. Token/coin (e.g., BTC, ETH)
        2. Alert condition (e.g., price above/below, whale movement)
        3. Threshold value (if applicable)
        4. Notification method (if specified)

        Return the information as a JSON with fields: token, condition, threshold, notification_method.
        """

        system_prompt = "You are a blockchain alert parameter extractor. Return only JSON with no explanation."

        response = self.call_llm(prompt, system_prompt)

        # Process the LLM response
        try:
            alert_params = json.loads(response)
        except:
            # Fallback if LLM response parsing fails
            alert_params = {
                "token": "Unknown",
                "condition": "Unknown",
                "threshold": "Unknown",
                "notification_method": "app"
            }

        # Check if AlarmAgent is available
        if "AlarmAgent" in self.connected_agents:
            alarm_agent = self.connected_agents["AlarmAgent"]
            alert_setup = alarm_agent.process({
                "action": "setup_alert",
                "parameters": alert_params
            })

            return {
                "response_type": "market_alert",
                "alert_setup": alert_setup,
                "success": True
            }
        else:
            return {
                "error": "AlarmAgent not available",
                "success": False
            }

    def _process_trading_action(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a trading action request"""
        user_message = input_data.get("user_message", "")

        # Use LLM to extract trading parameters
        prompt = f"""
        Extract trading parameters from the following user request:

        User request: "{user_message}"

        Extract the following information:
        1. Action type (buy/sell)
        2. Token/coin (e.g., BTC, ETH)
        3. Amount (in tokens or USD)
        4. Price (limit price if applicable)
        5. Trading venue (e.g., binance, wallet)

        Return the information as a JSON with fields: action_type, token, amount, price, venue.
        """

        system_prompt = "You are a blockchain trading parameter extractor. Return only JSON with no explanation."

        response = self.call_llm(prompt, system_prompt)

        # Process the LLM response
        try:
            trading_params = json.loads(response)
        except:
            # Fallback if LLM response parsing fails
            trading_params = self._fallback_trading_params(user_message)

        # Check if AutoTradeAgent is available
        if "AutoTradeAgent" in self.connected_agents:
            auto_trade_agent = self.connected_agents["AutoTradeAgent"]
            trade_result = auto_trade_agent.process({
                "action": "execute_trade",
                "parameters": trading_params
            })

            return {
                "response_type": "trading_action",
                "trade_result": trade_result,
                "success": True
            }
        else:
            return {
                "error": "AutoTradeAgent not available",
                "success": False
            }

    def _process_data_query(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a database query request using Text2SQL"""
        user_message = input_data.get("user_message", "")

        # Check if Text2SQLAgent is available
        if "Text2SQLAgent" not in self.connected_agents:
            return {
                "error": "Text2SQLAgent not available",
                "success": False
            }

        # Send the query to Text2SQLAgent for processing
        text2sql_agent = self.connected_agents["Text2SQLAgent"]
        query_result = text2sql_agent.process({
            "query": user_message
        })

        # If the query was successful, process the results
        if query_result.get("status") == "success":
            # Format the results for display
            formatted_results = self._format_query_results(query_result.get("results", []))

            return {
                "response_type": "data_query",
                "query": user_message,
                "sql_query": query_result.get("sql_query", ""),
                "results": formatted_results,
                "success": True
            }
        else:
            return {
                "response_type": "data_query",
                "error": query_result.get("message", "Failed to execute query"),
                "success": False
            }

    def _format_query_results(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Format query results for display"""
        if not results:
            return {
                "count": 0,
                "data": [],
                "summary": "No results found."
            }

        # Format the data for display
        formatted_data = results

        # Generate a summary of the results
        count = len(results)

        # Generate a summary using LLM if there are many results
        summary = ""
        if count > 0:
            # Limit the number of results for the prompt to avoid token limits
            sample_results = results[:min(10, count)]

            prompt = f"""
            Summarize the following query results in 1-2 sentences:

            Number of results: {count}
            Sample results: {json.dumps(sample_results, indent=2)}

            Provide a brief, informative summary of what these results show.
            """

            system_prompt = "You are a data analyst summarizing query results. Be concise and informative."

            summary = self.call_llm(prompt, system_prompt)
        else:
            summary = "No results found."

        return {
            "count": count,
            "data": formatted_data,
            "summary": summary.strip()
        }

    def _fallback_trading_params(self, user_message: str) -> Dict[str, Any]:
        """Generate fallback trading parameters from user message"""
        # Simple keyword-based parameter extraction
        action_type = "buy"
        if any(keyword in user_message.lower() for keyword in ["sell", "卖出", "卖", "出售"]):
            action_type = "sell"

        # Try to extract token
        token = "BTC"  # Default
        tokens = ["BTC", "ETH", "BNB", "SOL", "DOGE", "ADA", "XRP", "MATIC", "AVAX", "DOT"]
        for t in tokens:
            if t.lower() in user_message.lower():
                token = t
                break

        # Default values for other parameters
        amount = "0.1"
        price = "market"
        venue = "binance"

        return {
            "action_type": action_type,
            "token": token,
            "amount": amount,
            "price": price,
            "venue": venue
        }

    def _extract_tx_hash(self, user_message: str) -> str:
        """Extract transaction hash from user message using LLM"""
        prompt = f"""
        Extract the Ethereum transaction hash (tx hash) from the following message.
        A tx hash is a 66-character string that starts with "0x" followed by 64 hexadecimal characters (0-9, a-f).

        Message: "{user_message}"

        Return only the tx hash if found. If no tx hash is found, return "Not found".
        """

        system_prompt = "You are a blockchain transaction hash extractor. Return only the transaction hash with no explanation."

        response = self.call_llm(prompt, system_prompt)

        # Clean up the response and check if it's a valid hash format
        hash_candidate = response.strip().replace('"', '').replace("'", "")

        if hash_candidate.startswith("0x") and len(hash_candidate) == 66:
            try:
                int(hash_candidate[2:], 16)  # Check if it's valid hex
                return hash_candidate
            except ValueError:
                return ""

        return ""

    def _check_for_alerts(self, clean_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check if any alerts should be triggered based on analysis"""
        alerts = []

        # Check for high importance insights or recommendations
        insights = clean_data.get("insights", [])
        recommendations = clean_data.get("recommendations", [])

        # Add alerts for high importance insights
        for insight in insights:
            if insight.get("importance", "medium") == "high":
                alerts.append({
                    "type": "insight_alert",
                    "source": insight.get("source", "Unknown"),
                    "content": insight.get("content", ""),
                    "priority": "high"
                })

        # Add alerts for high priority recommendations
        for rec in recommendations:
            if rec.get("priority", "medium") == "high":
                alerts.append({
                    "type": "recommendation_alert",
                    "action": rec.get("action", ""),
                    "priority": "high"
                })

        # If AlarmAgent is available, send alerts
        if alerts and "AlarmAgent" in self.connected_agents:
            alarm_agent = self.connected_agents["AlarmAgent"]
            for alert in alerts:
                try:
                    alarm_agent.process({
                        "action": "send_alert",
                        "alert_data": alert
                    })
                except Exception as e:
                    print(f"Error sending alert: {str(e)}")

        return alerts

    def _check_for_trading_actions(self, clean_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check if any trading actions should be taken based on analysis"""
        trading_actions = []

        # Extract recommendations related to trading
        recommendations = clean_data.get("recommendations", [])

        # Check if any recommendation suggests a trading action
        for rec in recommendations:
            action = rec.get("action", "").lower()

            # Check if this is a trading-related recommendation
            if any(keyword in action for keyword in ["buy", "sell", "trade", "limit", "market"]):
                # Extract trading parameters
                trading_params = self._extract_trading_params_from_recommendation(rec.get("action", ""))

                if trading_params:
                    trading_actions.append({
                        "type": "recommended_trade",
                        "params": trading_params,
                        "source": rec.get("source", "analysis"),
                        "priority": rec.get("priority", "medium")
                    })

        # If AutoTradeAgent is available and there are high priority trades, execute them
        if trading_actions and "AutoTradeAgent" in self.connected_agents:
            auto_trade_agent = self.connected_agents["AutoTradeAgent"]

            for action in trading_actions:
                if action.get("priority") == "high":
                    try:
                        auto_trade_agent.process({
                            "action": "execute_trade",
                            "parameters": action.get("params", {})
                        })
                    except Exception as e:
                        print(f"Error executing trade: {str(e)}")

        return trading_actions

    def _extract_trading_params_from_recommendation(self, recommendation: str) -> Dict[str, Any]:
        """Extract trading parameters from a recommendation string using LLM"""
        if not recommendation:
            return None

        prompt = f"""
        Extract trading parameters from the following recommendation:

        Recommendation: "{recommendation}"

        Extract the following information if present:
        1. Action type (buy/sell)
        2. Token/coin (e.g., BTC, ETH)
        3. Amount (in tokens or USD)
        4. Price (limit price if applicable)

        Return the information as a JSON with fields: action_type, token, amount, price.
        If any field is not present in the recommendation, use a reasonable default value.
        """

        system_prompt = "You are a blockchain trading parameter extractor. Return only JSON with no explanation."

        response = self.call_llm(prompt, system_prompt)

        # Process the LLM response
        try:
            trading_params = json.loads(response)
            # Add default venue
            trading_params["venue"] = "auto"
            return trading_params
        except:
            # Return None if parsing fails
            return None
