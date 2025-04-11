from .abstract_client import AbstractClient
import requests
import os
from dotenv import load_dotenv
from typing import Optional

class DeepSeekClient(AbstractClient):
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv("DEEPSEEK_API_KEY")
        self.base_url = "https://api.deepseek.com/v1"
        self.model = "deepseek-chat"  # Can be configured via settings
    
    def get_response(self, system_prompt: str, user_prompt: str) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 2000
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            raise Exception(f"DeepSeek API request failed: {str(e)}")
    
    def filter_command(self, response: str) -> str:
        """Extracts the command from DeepSeek's response"""
        # DeepSeek might format commands differently than OpenAI
        import re
        
        # Try to find code blocks first
        code_block_match = re.search(r"```(?:bash)?\n?(.*?)\n?```", response, re.DOTALL)
        if code_block_match:
            return code_block_match.group(1).strip()
        
        # Then try inline code
        inline_code_match = re.search(r"`([^`]+)`", response)
        if inline_code_match:
            return inline_code_match.group(1).strip()
        
        # Finally, look for quoted commands
        quoted_match = re.search(r'"(.*?)"|\'(.*?)\'', response)
        if quoted_match:
            return quoted_match.group(1) or quoted_match.group(2)
        
        # If no special formatting found, return first non-empty line
        lines = [line.strip() for line in response.split('\n') if line.strip()]
        return lines[0] if lines else ""