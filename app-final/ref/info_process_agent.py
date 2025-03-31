from typing import Dict, Any, List
from base_agent import BaseAgent
from api_caller import api_caller

class InfoProcessAgent(BaseAgent):
    def __init__(self, name: str = "InfoProcessAgent", llm_model: str = None):
        super().__init__(name, llm_model)
        # Initialize connected specialized agents
        self.specialized_agents = {}

    def register_agent(self, agent_name: str, agent_instance: BaseAgent):
        """Register a specialized agent to receive data"""
        self.specialized_agents[agent_name] = agent_instance
        print(f"Agent {agent_name} registered with {self.name}")

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process blockchain transaction data and extract key information.
        This is the only agent that connects directly with blockchain APIs.

        Args:
            input_data: Dictionary containing transaction data or hash

        Returns:
            Processed transaction information with data distributed to specialized agents
        """
        # If input contains only a transaction hash, fetch the transaction data
        if 'tx_hash' in input_data and len(input_data) <= 2:  # Allow tx_hash and optional network
            network = input_data.get('network', 'ethereum')
            tx_data = self._fetch_transaction(input_data['tx_hash'], network)
        else:
            tx_data = input_data

        # Extract basic transaction information
        processed_data = self._extract_basic_info(tx_data)

        # Enrich with additional blockchain data
        processed_data = self._enrich_with_additional_data(processed_data)

        # Distribute data to specialized agents
        agent_responses = self._distribute_to_agents(processed_data)

        # Combine all data into final response
        result = {
            "transaction_data": processed_data,
            "agent_responses": agent_responses
        }

        return result

    def _fetch_transaction(self, tx_hash: str, network: str = "ethereum") -> Dict[str, Any]:
        """Fetch transaction data from blockchain API"""
        blockchain_api_params = {
            "method": "getTransaction",
            "tx_hash": tx_hash,
            "network": network
        }

        # Call blockchain API using api_caller
        response = api_caller(
            "blockchain",
            endpoint=f"{self.config.get('BLOCKCHAIN_API_URL', '')}/api",
            api_key=self.config.get('BLOCKCHAIN_API_KEY', ''),
            params=blockchain_api_params,
            agent_name=self.name
        )

        # Log the transaction data
        if self.interceptor:
            self.interceptor.intercept_message(
                self.name,
                "System",
                f"Transaction data fetched for {tx_hash}",
                "blockchain_data"
            )

        return response

    def _extract_basic_info(self, tx_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract basic information from transaction data"""
        # Use LLM to help parse complex transaction data if needed
        if 'input' in tx_data and len(tx_data.get('input', '')) > 10:
            method = self._parse_transaction_method(tx_data)
        else:
            method = "transfer"  # Simple ETH/token transfer

        # Basic extraction of transaction details
        info = {
            "tx_hash": tx_data.get("hash", ""),
            "sender": tx_data.get("from", ""),
            "receiver": tx_data.get("to", ""),
            "value": tx_data.get("value", "0"),
            "method": method,
            "timestamp": tx_data.get("timestamp", ""),
            "block_number": tx_data.get("blockNumber", ""),
            "network": tx_data.get("network", "ethereum"),
            "gas": tx_data.get("gas", ""),
            "gas_price": tx_data.get("gasPrice", ""),
            "nonce": tx_data.get("nonce", ""),
            "input_data": tx_data.get("input", ""),
            "token_name": "ETH"  # Default, will be updated if it's a token transfer
        }

        # If it's a token transfer, get token details
        if method == "transfer" and len(tx_data.get('input', '')) > 10:
            token_info = self._get_token_info(tx_data.get("to", ""), info["network"])
            info["token_name"] = token_info.get("name", "Unknown Token")
            info["token_symbol"] = token_info.get("symbol", "???")
            info["token_decimals"] = token_info.get("decimals", "18")

            # Try to parse token amount from input data
            # This is simplified, in reality would need proper ABI decoding
            info["token_amount"] = "Unknown Amount"

        return info

    def _parse_transaction_method(self, tx_data: Dict[str, Any]) -> str:
        """Parse transaction method from input data using LLM"""
        input_data = tx_data.get('input', '')
        if not input_data or input_data == '0x':
            return "transfer"

        prompt = f"""
        Parse the following blockchain transaction input data and identify the method being called:

        Input data: {input_data}
        From: {tx_data.get('from', '')}
        To: {tx_data.get('to', '')}
        Value: {tx_data.get('value', '0')}

        Return just the name of the method (e.g., "transfer", "swap", "approve", "addLiquidity", etc.)
        """

        response = self.call_llm(prompt)
        return response.strip()

    def _get_token_info(self, token_address: str, network: str = "ethereum") -> Dict[str, Any]:
        """Get token information for a given token contract address"""
        token_info_params = {
            "method": "getTokenInfo",
            "token_address": token_address,
            "network": network
        }

        response = api_caller(
            "blockchain",
            endpoint=f"{self.config.get('BLOCKCHAIN_API_URL', '')}/api",
            api_key=self.config.get('BLOCKCHAIN_API_KEY', ''),
            params=token_info_params,
            agent_name=self.name
        )

        return response

    def _enrich_with_additional_data(self, tx_info: Dict[str, Any]) -> Dict[str, Any]:
        """Enrich transaction data with additional blockchain information"""
        # Get sender balance
        sender_balance = self._get_address_balance(tx_info.get("sender", ""), tx_info.get("network", "ethereum"))
        tx_info["sender_balance"] = sender_balance.get("balance", "0")

        # Get receiver balance
        receiver_balance = self._get_address_balance(tx_info.get("receiver", ""), tx_info.get("network", "ethereum"))
        tx_info["receiver_balance"] = receiver_balance.get("balance", "0")

        # Add additional data as needed
        # ...

        return tx_info

    def _get_address_balance(self, address: str, network: str = "ethereum") -> Dict[str, Any]:
        """Get balance for a given address"""
        balance_params = {
            "method": "getBalance",
            "address": address,
            "network": network
        }

        response = api_caller(
            "blockchain",
            endpoint=f"{self.config.get('BLOCKCHAIN_API_URL', '')}/api",
            api_key=self.config.get('BLOCKCHAIN_API_KEY', ''),
            params=balance_params,
            agent_name=self.name
        )

        return response

    def _distribute_to_agents(self, processed_data: Dict[str, Any]) -> Dict[str, Any]:
        """Distribute processed data to connected specialized agents"""
        agent_responses = {}

        # List of specialized agents that should receive data
        target_agents = [
            "CEXWithdrawAgent",
            "WhaleAgent",
            "TxAgent",
            "ContractMonitorAgent",
            "BasicInfoAgent"
        ]

        # Send data to each connected agent
        for agent_name in target_agents:
            if agent_name in self.specialized_agents:
                agent = self.specialized_agents[agent_name]

                # Log data distribution
                if self.interceptor:
                    self.interceptor.intercept_message(
                        self.name,
                        agent_name,
                        f"Distributing data for tx {processed_data.get('tx_hash', '')}",
                        "data_distribution"
                    )

                # Call the agent's process method with the transaction data
                try:
                    agent_response = agent.process(processed_data)
                    agent_responses[agent_name] = agent_response
                except Exception as e:
                    agent_responses[agent_name] = {
                        "error": f"Error processing data: {str(e)}"
                    }

                    # Log error
                    if self.interceptor:
                        self.interceptor.intercept_message(
                            self.name,
                            agent_name,
                            f"Error distributing data: {str(e)}",
                            "error"
                        )
            else:
                agent_responses[agent_name] = {
                    "error": f"Agent {agent_name} not connected"
                }

        return agent_responses
