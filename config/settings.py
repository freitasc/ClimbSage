import os
from dotenv import load_dotenv
from pathlib import Path
from typing import Optional, Dict, Any

class Settings:
    def __init__(self):
        # Load environment variables
        env_path = Path('.') / '.env'
        load_dotenv(dotenv_path=env_path)

        # Core settings
        self.DEBUG: bool = self._get_bool('DEBUG', False)
        self.MAX_REQUESTS: int = self._get_int('MAX_REQUESTS', 10)
        self.DEFAULT_TIMEOUT: int = self._get_int('DEFAULT_TIMEOUT', 6)
        
        # AI Provider settings
        self.AI_PROVIDER: str = self._get_str('AI_PROVIDER', 'openai')
        self.OPENAI_API_KEY: Optional[str] = self._get_str('OPENAI_API_KEY')
        self.DEEPSEEK_API_KEY: Optional[str] = self._get_str('DEEPSEEK_API_KEY')
        self.OPENAI_MODEL: str = self._get_str('OPENAI_MODEL', 'gpt-3.5-turbo')
        self.DEEPSEEK_MODEL: str = self._get_str('DEEPSEEK_MODEL', 'deepseek-chat')

        # Command execution settings
        self.DEFAULT_SHELL: str = self._get_str('DEFAULT_SHELL', '/bin/sh')
        self.SSH_PORT: int = self._get_int('SSH_PORT', 22)

    def _get_str(self, key: str, default: Optional[str] = None) -> Optional[str]:
        return os.getenv(key, default)

    def _get_int(self, key: str, default: int) -> int:
        try:
            return int(os.getenv(key, str(default)))
        except ValueError:
            return default

    def _get_bool(self, key: str, default: bool) -> bool:
        val = os.getenv(key, str(default)).lower()
        return val in ('true', '1', 't', 'y', 'yes')

    def get_ai_config(self, provider: Optional[str] = None) -> Dict[str, Any]:
        provider = provider or self.AI_PROVIDER
        if provider == 'openai':
            return {
                'api_key': self.OPENAI_API_KEY,
                'model': self.OPENAI_MODEL
            }
        elif provider == 'deepseek':
            return {
                'api_key': self.DEEPSEEK_API_KEY,
                'model': self.DEEPSEEK_MODEL
            }
        else:
            raise ValueError(f"Unsupported AI provider: {provider}")

# Singleton instance
settings = Settings()