from .openai_client import OpenAIClient
from .deepseek_client import DeepSeekClient  # Implement similarly

def get_ai_provider(name: str):
    providers = {
        'openai': OpenAIClient,
        'deepseek': DeepSeekClient
    }
    return providers[name.lower()]()