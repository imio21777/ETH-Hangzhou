import os
import json
import configparser
import time
from typing import Dict, Any, Optional

class BaseAgent:
    def __init__(self, name: str, llm_model: str = None):
        """
        Initialize a base agent.

        Args:
            name: The name of the agent
            llm_model: The large language model to use (defaults to config value)
        """
        self.name = name
        self.config = self._load_config()
        self.llm_model = llm_model if llm_model else self.config.get('LLM_MODEL', 'gpt-4o-2024-05-13')
        
        # 获取延时配置
        try:
            self.delay_time = float(self.config.get('DELAY_TIME', '0'))
        except (ValueError, TypeError):
            self.delay_time = 0.0

        # Try to import interceptor
        try:
            from agent_interceptor import interceptor
            self.interceptor = interceptor
        except ImportError:
            self.interceptor = None
            print(f"Agent {name}: Interceptor not available")

    def _load_config(self) -> Dict[str, str]:
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

                print(f"Config loaded for {self.name}")
            except Exception as e:
                print(f"Error loading config: {e}")
        else:
            print(f"Config file not found at {config_path}")

        return config

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process input data and return output. This method should be overridden by subclasses.
        Standard format for input and output must be followed.

        Args:
            input_data: The input data to process in standardized format

        Returns:
            The processed output data in standardized format
        """
        raise NotImplementedError("Subclasses must implement this method")

    def call_llm(self, prompt: str, system_prompt: str = None) -> str:
        """
        Call LLM model with prompt

        Args:
            prompt: The main user prompt
            system_prompt: System instructions (optional)

        Returns:
            The model's response as a string
        """
        # Import api_caller
        from api_caller import api_caller

        # Record LLM call
        if self.interceptor:
            self.interceptor.intercept_message(
                self.name,
                "LLM",
                f"Prompt: {prompt[:100]}{'...' if len(prompt) > 100 else ''}",
                "llm_request"
            )

        # Build messages list
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        # Prepare API parameters
        params = {
            "model": self.llm_model,
            "messages": messages,
            "temperature": float(self.config.get('LLM_TEMPERATURE', 0.7)),
            "max_tokens": int(self.config.get('LLM_MAX_TOKENS', 1000))
        }

        # Call API
        try:
            response = api_caller(
                "llm_api",
                self.config.get('LLM_BASE_URL', "https://api2.aigcbest.top/v1") + "/chat/completions",
                self.config.get('LLM_API_KEY', ""),
                params,
                self.name  # Pass agent name
            )

            # Extract content
            result = response.get("content", "")

            # Record LLM response
            if self.interceptor:
                self.interceptor.intercept_message(
                    "LLM",
                    self.name,
                    f"Response: {result[:100]}{'...' if len(result) > 100 else ''}",
                    "llm_response"
                )
                
            # 添加代理内部处理延时
            if self.delay_time > 0:
                print(f"代理{self.name}处理延时: {self.delay_time}秒")
                time.sleep(self.delay_time)

            return result

        except Exception as e:
            error_message = f"Error calling LLM: {str(e)}"
            print(error_message)

            # Record error
            if self.interceptor:
                self.interceptor.intercept_message(
                    "LLM",
                    self.name,
                    error_message,
                    "error"
                )

            return "Error: Unable to get response from language model."
