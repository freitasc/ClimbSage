class PrivEscPrompt:
    def __init__(self, username: str, password: str, system: str, target_user: str):
        self.username = username
        self.password = password
        self.system = system
        self.target_user = target_user
        self.history = []
        self.facts = []
        self.hints = []
        self.avoids = []
        self.tools_data = {}
    
    def add_tool_data(self, tool_name: str, data: str):
        self.tools_data[tool_name] = data
    
    def add_history(self, command: str, output: str = ""):
        if not any(entry["command"] == command for entry in self.history):
            self.history.append({"command": command, "output": output})
    
    def generate_prompt(self) -> str:
        prompt = [
            f"You are user '{self.username}' (password: '{self.password}') on {self.system}.",
            f"Goal: Become '{self.target_user}' through privilege escalation.",
            "\n### System Information:"
        ]
        
        if self.tools_data:
            for tool, data in self.tools_data.items():
                prompt.append(f"\n{tool} output:\n{data}")
        
        if self.history:
            prompt.append("\n### Command History:")
            for entry in self.history:
                prompt.append(f"$ {entry['command']}")
                if entry['output']:
                    prompt.append(entry['output'])
        
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