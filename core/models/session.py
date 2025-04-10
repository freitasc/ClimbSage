import time
from typing import Optional
from core.utils.root_detector import RootDetector
from core.utils.timer import GlobalTimer
from core.models.prompt import PrivEscPrompt

class Session:
    def __init__(self, username: str, password: str, system: str, target_user: str, 
                 ai_provider, command_executor, max_requests: int = 10):
        self.prompt = PrivEscPrompt(username, password, system, target_user)
        self.ai_provider = ai_provider
        self.command_executor = command_executor
        self.max_requests = max_requests
        self.hostname = "target"
        self.running = False
    
    def run(self):
        self.running = True
        GlobalTimer.start()
        
        try:
            # Run automated privilege escalation
            for i in range(self.max_requests):
                if not self.running:
                    break
                
                print(f"\n[AI Request #{i+1}]")
                prompt = self.prompt.generate_prompt()
                print(f"[PROMPT]\n{prompt}\n")
                
                response = self.ai_provider.get_response(
                    "You are an experienced pentester.",
                    prompt
                )
                
                command = self.ai_provider.filter_command(response)
                print(f"[COMMAND] {command}")
                
                output = self.command_executor.execute(command)
                print(f"[OUTPUT]\n{output}")
                
                self.prompt.add_history(command, output)
                
                if RootDetector.got_root(self.hostname, output):
                    print("\n[SUCCESS] Root access achieved!")
                    summary = self._generate_summary()
                    print(f"\n[SUMMARY]\n{summary}")
                    break
                
                time.sleep(1)  # Rate limiting
            
        except KeyboardInterrupt:
            print("\n[INFO] Session stopped by user")
        finally:
            GlobalTimer.stop("Privilege escalation session")
            self.running = False
    
    def _generate_summary(self) -> str:
        summary = "Privilege Escalation Summary:\n\n"
        summary += "Commands executed:\n"
        for entry in self.prompt.history:
            summary += f"$ {entry['command']}\n"
            if entry['output']:
                summary += f"{entry['output']}\n\n"
        return summary