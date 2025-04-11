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
        self.last_output = ""
        self.last_command = ""
    
    def add_system_info(self, info: str):
        if info not in self.system_info:
            self.system_info.append(info)

    def add_command_history(self, command: str):
        if command not in self.command_history:
            self.command_history.append(command)
    
    def add_hint(self, hint: str):
        if hint not in self.hints:
            self.hints.append(hint)
    
    def add_fact(self, fact: str):
        if fact not in self.facts:
            self.facts.append(fact)
    
    def add_avoid(self, avoid: str):
        if avoid not in self.avoids:
            self.avoids.append(avoid)
    
    def clear(self):
        self.system_info.clear()
        self.command_history.clear()
        self.facts.clear()
        self.hints.clear()
        self.avoids.clear()
    
    def generate_prompt(self) -> str:
        prompt = [
            f"You are user '{self.username}' (password: '{self.password}') on {self.system}.",
            f"Goal: Become '{self.target_user}' through privilege escalation.",
            f"Provide ONLY the next command or input, no explanations.",
            f"If you have a password, use it to escalate privileges.",
            f"Use the following information to assist in your task:"
        ]
        
        if self.last_command:
            prompt.append(f"\n### Last Command: {self.last_command}")
            
        if self.last_output:
            prompt.append(f"\n### Last Output: {self.last_output}")
        
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
        
        return "\n".join(prompt)