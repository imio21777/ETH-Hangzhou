from typing import Dict, Any, List
import random
from base_agent import BaseAgent
from api_caller import api_caller

class CEXWithdrawAgent(BaseAgent):
    def __init__(self, name: str = "CEXWithdrawAgent", llm_model: str = None):
        super().__init__(name, llm_model)

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process transactions related to CEX withdrawals.

        Args:
            input_data: Transaction data processed by InfoProcessAgent

        Returns:
            Analysis of the CEX withdrawal transaction
        """
        if not input_data.get("isCEX", False):
            return {"relevance": "low", "details": "Not a CEX transaction"}

        sender = input_data.get("sender", "")
        receiver = input_data.get("receiver", "")
        amount = input_data.get("value", "0")
        token = input_data.get("token_name", "ETH")

        # Prepare prompt for analysis
        prompt = f"""
        Analyze this transaction that involves a centralized exchange (CEX):

        Transaction details:
        - Sender: {sender}
        - Receiver: {receiver}
        - Amount: {amount} {token}
        - Method: {input_data.get("method", "transfer")}
        - Timestamp: {input_data.get("timestamp", "")}

        Determine:
        1. If this is a withdrawal from a CEX (exchange to user)
        2. The significance of the withdrawal amount
        3. Any potential impact on the market

        Return your analysis as a JSON with fields: isWithdrawal (boolean), significance (string: "low", "medium", "high"),
        potentialImpact (string), and reasoning (string).
        """

        system_prompt = "You are a blockchain CEX activity analyzer. Return only JSON with no explanation."

        response = self.call_llm(prompt, system_prompt)

        # Process the LLM response
        try:
            analysis = eval(response)
        except:
            # Fallback if LLM response parsing fails
            analysis = {
                "isWithdrawal": receiver != sender,
                "significance": "medium" if float(amount) > 1000 else "low",
                "potentialImpact": "minimal",
                "reasoning": "Automated fallback analysis"
            }

        # Add original transaction data for reference
        analysis["original_tx"] = {
            "tx_hash": input_data.get("tx_hash", ""),
            "sender": sender,
            "receiver": receiver,
            "amount": amount,
            "token": token
        }

        return analysis


class WhaleAgent(BaseAgent):
    def __init__(self, name: str = "WhaleAgent", llm_model: str = None):
        super().__init__(name, llm_model)

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process transactions involving whale accounts.

        Args:
            input_data: Transaction data processed by InfoProcessAgent

        Returns:
            Analysis of the whale transaction
        """
        if not input_data.get("isWhale", False):
            return {"relevance": "low", "details": "Not a whale transaction"}

        sender = input_data.get("sender", "")
        receiver = input_data.get("receiver", "")
        amount = input_data.get("value", "0")
        token = input_data.get("token_name", "ETH")

        # Get historical transactions for context
        historical_data = self._get_historical_transactions(sender)

        # Prepare prompt for analysis
        prompt = f"""
        Analyze this transaction involving a whale account:

        Transaction details:
        - Sender: {sender}
        - Receiver: {receiver}
        - Amount: {amount} {token}
        - Method: {input_data.get("method", "transfer")}
        - Timestamp: {input_data.get("timestamp", "")}

        Recent historical transactions from this whale:
        {historical_data}

        Determine:
        1. The significance of this whale movement
        2. Potential market impact
        3. Possible reasoning behind the transaction

        Return your analysis as a JSON with fields: significance (string: "low", "medium", "high"),
        marketImpact (string), reasoning (string), and recommendedAction (string).
        """

        system_prompt = "You are a blockchain whale activity analyzer. Return only JSON with no explanation."

        response = self.call_llm(prompt, system_prompt)

        # Process the LLM response
        try:
            analysis = eval(response)
        except:
            # Fallback if LLM response parsing fails
            analysis = {
                "significance": "high" if float(amount) > 100000 else "medium",
                "marketImpact": "Could cause price volatility",
                "reasoning": "Large transfer of funds, typical whale accumulation or distribution",
                "recommendedAction": "Monitor for additional movements"
            }

        # Add original transaction data for reference
        analysis["original_tx"] = {
            "tx_hash": input_data.get("tx_hash", ""),
            "sender": sender,
            "receiver": receiver,
            "amount": amount,
            "token": token
        }

        return analysis

    def _get_historical_transactions(self, address: str) -> str:
        """Get historical transactions for a given address"""
        # In a real implementation, this would query the blockchain
        # Here we'll return mock data
        return "Previous transactions show a pattern of accumulation over the last 30 days"


class TxAgent(BaseAgent):
    def __init__(self, name: str = "TxAgent", llm_model: str = None):
        super().__init__(name, llm_model)

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process transactions to identify frequent senders/receivers.

        Args:
            input_data: Transaction data processed by InfoProcessAgent

        Returns:
            Analysis of transaction patterns
        """
        sender = input_data.get("sender", "")
        receiver = input_data.get("receiver", "")

        # Get transaction frequency data
        sender_frequency = self._get_address_tx_frequency(sender)
        receiver_frequency = self._get_address_tx_frequency(receiver)

        # Prepare prompt for analysis
        prompt = f"""
        Analyze the transaction frequency patterns:

        Transaction details:
        - Sender: {sender} (frequency: {sender_frequency} tx/day)
        - Receiver: {receiver} (frequency: {receiver_frequency} tx/day)
        - Method: {input_data.get("method", "transfer")}

        Determine:
        1. If either address shows unusual transaction frequency
        2. Potential patterns of behavior
        3. Risk assessment based on transaction patterns

        Return your analysis as a JSON with fields: unusualActivity (boolean),
        pattern (string), riskLevel (string: "low", "medium", "high"), and notes (string).
        """

        system_prompt = "You are a blockchain transaction pattern analyzer. Return only JSON with no explanation."

        response = self.call_llm(prompt, system_prompt)

        # Process the LLM response
        try:
            analysis = eval(response)
        except:
            # Fallback if LLM response parsing fails
            analysis = {
                "unusualActivity": sender_frequency > 20 or receiver_frequency > 20,
                "pattern": "High frequency trading" if sender_frequency > 20 else "Normal activity",
                "riskLevel": "high" if sender_frequency > 50 or receiver_frequency > 50 else "low",
                "notes": "Automated pattern analysis"
            }

        # Add frequency data for reference
        analysis["frequency_data"] = {
            "sender_address": sender,
            "sender_tx_per_day": sender_frequency,
            "receiver_address": receiver,
            "receiver_tx_per_day": receiver_frequency
        }

        return analysis

    def _get_address_tx_frequency(self, address: str) -> int:
        """Get transaction frequency for an address (tx per day)"""
        # In a real implementation, this would query the blockchain
        # Here we'll return mock data based on first character of address
        try:
            # Use the first hex character as a number 0-15
            first_char = address[2:3].lower()
            if first_char.isdigit():
                return int(first_char) * 5  # 0-45 tx/day
            else:
                # a=10, b=11, ..., f=15
                return (ord(first_char) - ord('a') + 10) * 5  # 50-75 tx/day
        except:
            return 10  # Default value


class ContractMonitorAgent(BaseAgent):
    def __init__(self, name: str = "ContractMonitorAgent", llm_model: str = None):
        super().__init__(name, llm_model)

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Monitor contract interactions and identify potential security issues.

        Args:
            input_data: Transaction data processed by InfoProcessAgent

        Returns:
            Analysis of contract interaction
        """
        # Check if this is a contract interaction
        method = input_data.get("method", "")
        if method == "transfer":
            return {"relevance": "low", "details": "Simple transfer, not a complex contract interaction"}

        contract_address = input_data.get("receiver", "")

        # Get contract information
        contract_info = self._get_contract_info(contract_address)

        # Prepare prompt for analysis
        prompt = f"""
        Analyze this contract interaction:

        Transaction details:
        - Sender: {input_data.get("sender", "")}
        - Contract: {contract_address}
        - Method called: {method}
        - Input data: {input_data.get("input_data", "0x")}

        Contract information:
        - Name: {contract_info.get("name", "Unknown")}
        - Type: {contract_info.get("type", "Unknown")}
        - Verified: {contract_info.get("verified", False)}
        - Audit status: {contract_info.get("audit_status", "Unknown")}

        Determine:
        1. Any security concerns with this interaction
        2. Potential impact of the operation
        3. Recommendation for similar future interactions

        Return your analysis as a JSON with fields: securityRisk (string: "low", "medium", "high"),
        impact (string), recommendation (string), and reasoning (string).
        """

        system_prompt = "You are a blockchain smart contract security analyzer. Return only JSON with no explanation."

        response = self.call_llm(prompt, system_prompt)

        # Process the LLM response
        try:
            analysis = eval(response)
        except:
            # Fallback if LLM response parsing fails
            analysis = {
                "securityRisk": "medium" if not contract_info.get("verified", False) else "low",
                "impact": "Contract interaction could modify state",
                "recommendation": "Proceed with caution" if contract_info.get("audit_status", "") != "Audited" else "Safe to proceed",
                "reasoning": "Automated security assessment"
            }

        # Add contract data for reference
        analysis["contract_data"] = {
            "address": contract_address,
            "name": contract_info.get("name", "Unknown"),
            "verified": contract_info.get("verified", False),
            "method_called": method
        }

        return analysis

    def _get_contract_info(self, contract_address: str) -> Dict[str, Any]:
        """Get information about a smart contract"""
        # In a real implementation, this would query the blockchain
        # Here we'll return mock data
        return {
            "name": f"Contract_{contract_address[:6]}",
            "type": "ERC20" if contract_address.startswith("0x7") else "DEX",
            "verified": contract_address.startswith("0x1") or contract_address.startswith("0x5"),
            "audit_status": "Audited" if contract_address.startswith("0x1") else "Unaudited"
        }


class BasicInfoAgent(BaseAgent):
    def __init__(self, name: str = "BasicInfoAgent", llm_model: str = None):
        super().__init__(name, llm_model)

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Provide basic information about coins and tokens.

        Args:
            input_data: Transaction data processed by InfoProcessAgent

        Returns:
            Enhanced information about the token/coin
        """
        token_name = input_data.get("token_name", "ETH")
        token_symbol = input_data.get("token_symbol", token_name)

        # Get token information
        token_info = self._get_token_market_info(token_symbol)

        # Prepare response
        coin_analysis = {
            "token_name": token_name,
            "token_symbol": token_symbol,
            "current_price_usd": token_info.get("price_usd", "Unknown"),
            "market_cap": token_info.get("market_cap", "Unknown"),
            "24h_volume": token_info.get("volume_24h", "Unknown"),
            "24h_change": token_info.get("change_24h", "Unknown"),
            "analysis": f"Token {token_symbol} shows {token_info.get('change_24h', '0')}% change in the last 24 hours"
        }

        # Add transaction context
        coin_analysis["tx_context"] = {
            "tx_hash": input_data.get("tx_hash", ""),
            "amount": input_data.get("value", "0"),
            "usd_value": float(input_data.get("value", "0")) * float(token_info.get("price_usd", "0").replace("$", "").replace(",", ""))
        }

        return coin_analysis

    def _get_token_market_info(self, token_symbol: str) -> Dict[str, Any]:
        """Get market information for a token"""
        # In a real implementation, this would query a price API
        # Here we'll return mock data
        return {
            "price_usd": f"${random.uniform(0.1, 50000):.2f}",
            "market_cap": f"${random.uniform(1000000, 500000000000):.2f}",
            "volume_24h": f"${random.uniform(10000, 10000000000):.2f}",
            "change_24h": f"{random.uniform(-15, 15):.2f}%"
        }
