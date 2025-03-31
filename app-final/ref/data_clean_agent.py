from typing import Dict, Any, List
from base_agent import BaseAgent
import json
import sqlite3
import os
import time

class DataCleanAgent(BaseAgent):
    def __init__(self, name: str = "DataCleanAgent", llm_model: str = None):
        super().__init__(name, llm_model)
        self.db_path = self.config.get('DB_PATH', 'blockchain_data.db')
        self._initialize_database()

    def _initialize_database(self):
        """Initialize the SQLite database with required tables"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Create transactions table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                tx_hash TEXT PRIMARY KEY,
                sender TEXT,
                receiver TEXT,
                value TEXT,
                token_name TEXT,
                token_symbol TEXT,
                method TEXT,
                timestamp TEXT,
                block_number TEXT,
                network TEXT,
                gas TEXT,
                gas_price TEXT,
                input_data TEXT,
                sender_balance TEXT,
                receiver_balance TEXT,
                processed_at TEXT
            )
            ''')

            # Create labels table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS labels (
                tx_hash TEXT,
                label_type TEXT,
                label_value TEXT,
                confidence REAL,
                source TEXT,
                PRIMARY KEY (tx_hash, label_type, source),
                FOREIGN KEY (tx_hash) REFERENCES transactions(tx_hash)
            )
            ''')

            # Create insights table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS insights (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tx_hash TEXT,
                insight_type TEXT,
                content TEXT,
                source TEXT,
                importance TEXT,
                timestamp TEXT,
                FOREIGN KEY (tx_hash) REFERENCES transactions(tx_hash)
            )
            ''')

            # Create recommendations table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS recommendations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tx_hash TEXT,
                action TEXT,
                priority TEXT,
                source TEXT,
                timestamp TEXT,
                FOREIGN KEY (tx_hash) REFERENCES transactions(tx_hash)
            )
            ''')

            # Create metrics table for numeric data
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS metrics (
                tx_hash TEXT,
                metric_name TEXT,
                metric_value REAL,
                source TEXT,
                timestamp TEXT,
                PRIMARY KEY (tx_hash, metric_name, source),
                FOREIGN KEY (tx_hash) REFERENCES transactions(tx_hash)
            )
            ''')

            conn.commit()
            print(f"Database initialized at {self.db_path}")
        except Exception as e:
            print(f"Error initializing database: {e}")
        finally:
            if conn:
                conn.close()

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Clean, normalize, and store data from other agents in the database.

        Args:
            input_data: Combined data from multiple agents

        Returns:
            Cleaned and normalized data
        """
        # Extract transaction data
        transaction_data = input_data.get("transaction_data", {})
        agent_responses = input_data.get("agent_responses", {})

        # Initialize clean data structure
        clean_data = {
            "transaction": {
                "hash": transaction_data.get("tx_hash", ""),
                "sender": transaction_data.get("sender", ""),
                "receiver": transaction_data.get("receiver", ""),
                "value": transaction_data.get("value", "0"),
                "token": transaction_data.get("token_name", "ETH"),
                "token_symbol": transaction_data.get("token_symbol", "ETH"),
                "method": transaction_data.get("method", "transfer"),
                "timestamp": transaction_data.get("timestamp", ""),
                "block_number": transaction_data.get("block_number", ""),
                "network": transaction_data.get("network", "ethereum")
            },
            "analysis": {
                "labels": {},
                "metrics": {}
            },
            "insights": [],
            "recommendations": []
        }

        # Process each agent's output
        for agent_name, agent_output in agent_responses.items():
            # Skip if there was an error with this agent
            if "error" in agent_output:
                continue

            # Extract insights and metrics from each agent
            self._process_agent_output(agent_name, agent_output, clean_data)

        # Store data in database
        self._store_in_database(clean_data, transaction_data)

        # Use LLM to generate a summary of the insights
        clean_data["summary"] = self._generate_summary(clean_data)

        return clean_data

    def _process_agent_output(self, agent_name: str, agent_output: Dict[str, Any], clean_data: Dict[str, Any]):
        """Process output from a specific agent and update clean_data"""
        if agent_name == "CEXWithdrawAgent":
            if agent_output.get("relevance", "low") != "low":
                clean_data["analysis"]["metrics"]["withdrawal_significance"] = agent_output.get("significance", "low")
                clean_data["insights"].append({
                    "source": "CEX Analysis",
                    "content": agent_output.get("reasoning", ""),
                    "importance": "high" if agent_output.get("significance", "low") == "high" else "medium"
                })
                if agent_output.get("potentialImpact", ""):
                    clean_data["insights"].append({
                        "source": "Market Impact",
                        "content": agent_output.get("potentialImpact", ""),
                        "importance": "medium"
                    })

                # Add CEX label
                clean_data["analysis"]["labels"]["isCEX"] = True

        elif agent_name == "WhaleAgent":
            if agent_output.get("relevance", "low") != "low":
                clean_data["analysis"]["metrics"]["whale_significance"] = agent_output.get("significance", "low")
                clean_data["insights"].append({
                    "source": "Whale Analysis",
                    "content": agent_output.get("reasoning", ""),
                    "importance": "high" if agent_output.get("significance", "low") == "high" else "medium"
                })
                clean_data["recommendations"].append({
                    "action": agent_output.get("recommendedAction", ""),
                    "priority": "high" if agent_output.get("significance", "low") == "high" else "medium",
                    "source": "WhaleAgent"
                })

                # Add Whale label
                clean_data["analysis"]["labels"]["isWhale"] = True

        elif agent_name == "TxAgent":
            clean_data["analysis"]["metrics"]["tx_frequency"] = agent_output.get("frequency", 0)
            clean_data["analysis"]["metrics"]["risk_level"] = agent_output.get("riskLevel", "low")

            if agent_output.get("unusualActivity", False):
                clean_data["insights"].append({
                    "source": "Transaction Pattern",
                    "content": agent_output.get("pattern", "") + " - " + agent_output.get("notes", ""),
                    "importance": "medium"
                })

        elif agent_name == "ContractMonitorAgent":
            if agent_output.get("relevance", "low") != "low":
                clean_data["analysis"]["metrics"]["security_risk"] = agent_output.get("securityRisk", "low")
                clean_data["insights"].append({
                    "source": "Contract Security",
                    "content": agent_output.get("reasoning", ""),
                    "importance": "high" if agent_output.get("securityRisk", "low") == "high" else "medium"
                })
                clean_data["recommendations"].append({
                    "action": agent_output.get("recommendation", ""),
                    "priority": "high" if agent_output.get("securityRisk", "low") == "high" else "medium",
                    "source": "ContractMonitorAgent"
                })

        elif agent_name == "BasicInfoAgent":
            clean_data["analysis"]["metrics"]["token_price"] = agent_output.get("current_price_usd", 0)
            clean_data["analysis"]["metrics"]["token_24h_change"] = agent_output.get("24h_change", 0)
            clean_data["insights"].append({
                "source": "Market Info",
                "content": agent_output.get("analysis", ""),
                "importance": "low"
            })

            # Add KOL label if applicable
            if agent_output.get("isKOL", False):
                clean_data["analysis"]["labels"]["isKOL"] = True

    def _store_in_database(self, clean_data: Dict[str, Any], raw_transaction_data: Dict[str, Any]):
        """Store cleaned data in SQLite database"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Store transaction data
            tx = clean_data["transaction"]
            cursor.execute('''
            INSERT OR REPLACE INTO transactions
            (tx_hash, sender, receiver, value, token_name, token_symbol, method, timestamp, block_number,
            network, gas, gas_price, input_data, sender_balance, receiver_balance, processed_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                tx["hash"],
                tx["sender"],
                tx["receiver"],
                tx["value"],
                tx["token"],
                tx.get("token_symbol", ""),
                tx["method"],
                tx["timestamp"],
                tx["block_number"],
                tx["network"],
                raw_transaction_data.get("gas", ""),
                raw_transaction_data.get("gas_price", ""),
                raw_transaction_data.get("input_data", ""),
                raw_transaction_data.get("sender_balance", ""),
                raw_transaction_data.get("receiver_balance", ""),
                str(int(time.time()))
            ))

            # Store labels
            for label_type, label_value in clean_data["analysis"]["labels"].items():
                cursor.execute('''
                INSERT OR REPLACE INTO labels
                (tx_hash, label_type, label_value, confidence, source)
                VALUES (?, ?, ?, ?, ?)
                ''', (
                    tx["hash"],
                    label_type,
                    str(label_value),
                    1.0,  # Default confidence
                    "agent_analysis"
                ))

            # Store metrics
            for metric_name, metric_value in clean_data["analysis"]["metrics"].items():
                # Convert metric value to float if possible
                try:
                    float_value = float(metric_value)
                except (ValueError, TypeError):
                    float_value = 0.0

                cursor.execute('''
                INSERT OR REPLACE INTO metrics
                (tx_hash, metric_name, metric_value, source, timestamp)
                VALUES (?, ?, ?, ?, ?)
                ''', (
                    tx["hash"],
                    metric_name,
                    float_value,
                    "agent_analysis",
                    str(int(time.time()))
                ))

            # Store insights
            for insight in clean_data["insights"]:
                cursor.execute('''
                INSERT INTO insights
                (tx_hash, insight_type, content, source, importance, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    tx["hash"],
                    "analysis",
                    insight["content"],
                    insight["source"],
                    insight.get("importance", "medium"),
                    str(int(time.time()))
                ))

            # Store recommendations
            for recommendation in clean_data["recommendations"]:
                cursor.execute('''
                INSERT INTO recommendations
                (tx_hash, action, priority, source, timestamp)
                VALUES (?, ?, ?, ?, ?)
                ''', (
                    tx["hash"],
                    recommendation["action"],
                    recommendation["priority"],
                    recommendation.get("source", "unknown"),
                    str(int(time.time()))
                ))

            conn.commit()
            print(f"Stored data for transaction {tx['hash']} in database")

        except Exception as e:
            print(f"Error storing data in database: {e}")
            if conn:
                conn.rollback()
        finally:
            if conn:
                conn.close()

    def _generate_summary(self, clean_data: Dict[str, Any]) -> str:
        """Generate a summary of the insights using LLM"""
        # Prepare data for summary generation
        transaction = clean_data["transaction"]
        insights = clean_data["insights"]
        recommendations = clean_data["recommendations"]

        insights_text = "\n".join([f"- {insight['source']}: {insight['content']}" for insight in insights])
        recommendations_text = "\n".join([f"- {rec['action']} (Priority: {rec['priority']})" for rec in recommendations])

        prompt = f"""
        Summarize the following blockchain transaction analysis:

        Transaction:
        - Hash: {transaction.get('hash', '')}
        - From: {transaction.get('sender', '')}
        - To: {transaction.get('receiver', '')}
        - Amount: {transaction.get('value', '0')} {transaction.get('token', 'ETH')}
        - Method: {transaction.get('method', 'transfer')}

        Insights:
        {insights_text}

        Recommendations:
        {recommendations_text}

        Provide a concise 1-2 sentence summary of the most important findings and their implications.
        """

        system_prompt = "You are a blockchain analyst assistant. Be concise and focus on key implications."

        response = self.call_llm(prompt, system_prompt)
        return response.strip()

    def query_database(self, sql_query: str) -> List[Dict[str, Any]]:
        """Execute a SQL query on the database and return results"""
        conn = None
        results = []

        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row  # This enables column access by name
            cursor = conn.cursor()

            cursor.execute(sql_query)
            rows = cursor.fetchall()

            # Convert rows to dictionaries
            for row in rows:
                results.append({key: row[key] for key in row.keys()})

        except Exception as e:
            print(f"Error executing query: {e}")
        finally:
            if conn:
                conn.close()

        return results
