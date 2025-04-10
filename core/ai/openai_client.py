from openai import OpenAI
import os
from dotenv import load_dotenv
from .ai_provider import AIProvider

class OpenAIClient(AIProvider):
    def __init__(self):
        load_dotenv()
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    def get_response(self, system_prompt: str, user_prompt: str) -> str:
        completion = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )
        return completion.choices[0].message.content.strip()
    
    def filter_command(self, response: str) -> str:
        # Implement OpenAI-specific command filtering
        import re
        pattern = r"```(?:bash\s)?(.*?)```|`(?:bash\s)?(.*?)`|'(.*?)'"
        matches = re.findall(pattern, response, re.DOTALL)
        commands = [cmd.strip() for group in matches for cmd in group if cmd.strip()]
        return commands[0] if commands else response.strip()