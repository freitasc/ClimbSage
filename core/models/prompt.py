class PrivEscPrompt:
    def __init__(self, username: str, password: str, system: str, target_user: str):
        self.username = username
        self.password = password
        self.system = system
        self.target_user = target_user
        self.system_info = []
        self.command_history = []
        self.facts = []
        self.hints = []
        self.avoids = []
    
    def add_command_history(self, command: str):
        if command not in self.command_history:
            self.command_history.append(command)
    
    def add_system_info(self, info: str):
        if info not in self.system_info:
            self.system_info.append(info)
    
    def generate_prompt(self) -> str:
        prompt = [
            f"You are user '{self.username}' (password: '{self.password}') on {self.system}.",
            f"Goal: Become '{self.target_user}' through privilege escalation.",
        ]
        
        if self.system_info:
            prompt.append("\n### System Information:")
            for info in self.system_info:
                prompt.append(f"- {info}")
        
        if self.command_history:
            prompt.append("\n### Command History:")
            for command in self.command_history:
                prompt.append(f"$ {command}")

        
        if self.facts:
            prompt.append("\n### Known Facts:")
            prompt.extend(f"- {fact}" for fact in self.facts)
        
        if self.hints:
            prompt.append("\n### Hints:")
            prompt.extend(f"- {hint}" for hint in self.hints)
        
        if self.avoids:
            prompt.append("\n### Avoid:")
            prompt.extend(f"- {avoid}" for avoid in self.avoids)
        
        prompt.append("\nProvide ONLY the next command to execute, no explanations.")
        return "\n".join(prompt)