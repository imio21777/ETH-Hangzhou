#!/usr/bin/env python
import os
import sys
import json
import time
import argparse
from typing import Dict, Any, List

# Import all agent classes
from base_agent import BaseAgent
from info_process_agent import InfoProcessAgent
from specialized_agents import CEXWithdrawAgent, WhaleAgent, TxAgent, ContractMonitorAgent, BasicInfoAgent
from data_clean_agent import DataCleanAgent
from central_agent import CentralAgent
from execution_agents import AutoTradeAgent, AlarmAgent, WalletAgent, CEXAgent
from text2sql import Text2SQLAgent

def initialize_agents():
    """Initialize all agents and establish connections between them."""

    # Initialize all agents with their default names
    info_process_agent = InfoProcessAgent()
    data_clean_agent = DataCleanAgent()
    central_agent = CentralAgent()

    # Initialize specialized agents
    cex_withdraw_agent = CEXWithdrawAgent()
    whale_agent = WhaleAgent()
    tx_agent = TxAgent()
    contract_monitor_agent = ContractMonitorAgent()
    basic_info_agent = BasicInfoAgent()

    # Initialize execution agents
    auto_trade_agent = AutoTradeAgent()
    alarm_agent = AlarmAgent()
    wallet_agent = WalletAgent()
    cex_agent = CEXAgent()

    # Initialize Text2SQL agent
    text2sql_agent = Text2SQLAgent()

    # Register specialized agents with info_process_agent
    info_process_agent.register_agent("CEXWithdrawAgent", cex_withdraw_agent)
    info_process_agent.register_agent("WhaleAgent", whale_agent)
    info_process_agent.register_agent("TxAgent", tx_agent)
    info_process_agent.register_agent("ContractMonitorAgent", contract_monitor_agent)
    info_process_agent.register_agent("BasicInfoAgent", basic_info_agent)

    # Register execution agents with auto_trade_agent
    auto_trade_agent.register_agent("WalletAgent", wallet_agent)
    auto_trade_agent.register_agent("CEXAgent", cex_agent)

    # Register all agents with central_agent
    central_agent.register_agent("InfoProcessAgent", info_process_agent)
    central_agent.register_agent("DataCleanAgent", data_clean_agent)
    central_agent.register_agent("AutoTradeAgent", auto_trade_agent)
    central_agent.register_agent("AlarmAgent", alarm_agent)
    central_agent.register_agent("Text2SQLAgent", text2sql_agent)

    # Return the central agent which will coordinate all operations
    return central_agent

def _load_delay_config() -> float:
    """从配置文件加载延时时间"""
    delay_time = 0.0
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.txt')

    if os.path.exists(config_path):
        try:
            with open(config_path, 'r') as file:
                for line in file:
                    line = line.strip()
                    # 跳过注释和空行
                    if not line or line.startswith('#'):
                        continue

                    # 解析键值对
                    if '=' in line and 'DELAY_TIME' in line:
                        key, value = line.split('=', 1)
                        if key.strip() == 'DELAY_TIME':
                            delay_time = float(value.strip().strip('"\''))
                            break
        except Exception as e:
            print(f"加载延时配置错误: {e}")
            
    return delay_time

def process_user_request(central_agent, user_request):
    """Process a user request through the central agent."""

    if isinstance(user_request, str):
        # Convert string request to proper input format
        input_data = {"user_message": user_request}
    else:
        # Assume it's already in the right format
        input_data = user_request

    # Process the request through the central agent
    result = central_agent.process(input_data)
    
    # 添加处理完成后的延时
    delay_time = _load_delay_config()
    if delay_time > 0:
        print(f"请求处理完成后延时: {delay_time}秒")
        time.sleep(delay_time)

    return result

def process_transaction(central_agent, tx_hash):
    """处理区块链交易分析，添加延时以便调试"""
    result = process_user_request(central_agent, {"tx_hash": tx_hash})
    
    # 添加交易处理后的额外延时
    delay_time = _load_delay_config()
    if delay_time > 0:
        print(f"交易处理完成后延时: {delay_time}秒")
        time.sleep(delay_time)
        
    return result

def main():
    """Main entry point for the CLI application."""
    parser = argparse.ArgumentParser(description="Blockchain Analytics and Trading Agent System")
    parser.add_argument("--request", "-r", type=str, help="User request as a string")
    parser.add_argument("--tx-hash", "-t", type=str, help="Transaction hash to analyze")
    parser.add_argument("--interactive", "-i", action="store_true", help="Run in interactive mode")
    parser.add_argument("--demo", "-d", action="store_true", help="Run with demo data")

    args = parser.parse_args()

    # Initialize all agents
    central_agent = initialize_agents()
    print("Agents initialized successfully!")

    if args.interactive:
        # Run in interactive mode
        print("=== Blockchain Analytics and Trading Agent System ===")
        print("Type 'exit' to quit")

        while True:
            user_input = input("\nEnter your request: ")

            if user_input.lower() in ["exit", "quit", "q"]:
                print("Exiting...")
                break

            # Process the user request
            try:
                result = process_user_request(central_agent, user_input)

                # Pretty print the result
                print("\nResult:")
                print(json.dumps(result, indent=2))
            except Exception as e:
                print(f"Error processing request: {str(e)}")

    elif args.request:
        # Process a single request from command line
        result = process_user_request(central_agent, args.request)
        print(json.dumps(result, indent=2))

    elif args.tx_hash:
        # Analyze a specific transaction
        result = process_transaction(central_agent, args.tx_hash)
        print(json.dumps(result, indent=2))

    else:
        # No arguments provided, show usage
        parser.print_help()

if __name__ == "__main__":
    main()
