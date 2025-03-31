# Blockchain Multi-Agent System

This project implements a multi-agent system for blockchain transaction monitoring, analysis, and automated trading based on predefined conditions. The system follows a modular architecture where specialized agents handle different aspects of blockchain data processing and decision-making.

## System Architecture

The system is composed of the following key components:

1. **Base Agent** - A superclass that all agents inherit from, providing common functionality.
2. **Info Process Agent** - Processes raw blockchain data and extracts key information.
3. **Specialized Agents**:
   - **CEX Withdraw Agent** - Analyzes centralized exchange withdrawals
   - **Whale Agent** - Monitors large holder (whale) activity
   - **TX Agent** - Analyzes transaction patterns
   - **Contract Monitor Agent** - Monitors smart contract interactions
   - **Basic Info Agent** - Provides information about coins/tokens
4. **Data Clean Agent** - Cleans and normalizes data from other agents
5. **Central Agent** - Coordinates between user input and other agents
6. **Execution Agents**:
   - **Alarm Agent** - Handles notifications
   - **Wallet Agent** - Executes blockchain transactions
   - **CEX Agent** - Interfaces with centralized exchanges

## Setup

1. Ensure you have Python 3.7+ installed.
2. Install the required dependencies (for a real implementation).
3. Configure your API keys in `config.txt`.

The current implementation uses mock API calls that output information to the console and return simulated data.

## Configuration

The system uses a `config.txt` file with the following format:

```
BASE_URL = "https://api2.aigcbest.top/v1"
API_KEY = "sk-NiMvTTja0AQMrEkNgOElafUVP6HnOcrBu0tJhfTeucBSJzU3"
MODEL = "claude-3-7-sonnet-20250219-thinking"
```

## Usage

### Running the Demo

```bash
python main.py --demo all
```

Demo options:
- `tx`: Run transaction analysis demo
- `alert`: Run market alert setup demo
- `trade`: Run trading action demo
- `all`: Run all demos (default)

### Transaction Analysis

To analyze a blockchain transaction:

```python
from main import create_agent_system, process_transaction

central_agent = create_agent_system()
result = process_transaction(central_agent, "0x7d3c5142ef8063322ad0815155a6627365a5b0548f1b488588b54bf6a242a7c8")
print(result)
```

### Setting Up Market Alerts

To set up a market alert:

```python
from main import create_agent_system, process_user_request

central_agent = create_agent_system()
result = process_user_request(central_agent, "Alert me when ETH price goes above $2500 by email")
print(result)
```

### Executing Trading Actions

To execute a trading action:

```python
from main import create_agent_system, process_user_request

central_agent = create_agent_system()
result = process_user_request(central_agent, "Buy 0.5 BTC on Binance when the price drops to $40,000")
print(result)
```

## Extending the System

### Adding a New Agent

1. Create a new class that inherits from `BaseAgent`
2. Implement the `process` method
3. Register your agent with the central agent:

```python
central_agent.register_agent("YourAgentName", your_agent_instance)
```

### Customizing API Calls

The system uses a unified `api_caller` function in `api_caller.py` to handle all API requests. For real implementations, modify this function to make actual API calls instead of returning mock data.

## Notes

This implementation is a demonstration of the architecture and does not make real API calls or execute actual blockchain transactions. In a production environment, you would need to:

1. Implement proper API calls
2. Add error handling and retry mechanisms
3. Set up secure key management
4. Add logging and monitoring
5. Implement proper authentication and authorization

## License

MIT
