import time
from typing import Optional
from core.utils.root_detector import RootDetector
from core.utils.timer import GlobalTimer
from core.models.prompt import PrivEscPrompt
from core.scanners.beroot import BeRootScanner
from core.scanners.linpeas import LinPEASScanner
from core.utils.logger import debug_logger
import re

class Session:
    def __init__(self, username: str, password: str, system: str, target_user: str, 
                 ai_provider, command_executor, max_requests: int = 10000):
        self.prompt = PrivEscPrompt(username, password, system, target_user)
        self.ai_provider = ai_provider
        self.command_executor = command_executor
        self.max_requests = max_requests
        self.hostname = "target"
        self.running = False
        self.scanners = {
            'beroot': BeRootScanner(),
            'linpeas': LinPEASScanner()
        }
    
    def run_scan(self, scan_name: str) -> str:
        if scan_name not in self.scanners:
            return f"Unknown scanner: {scan_name}"
        
        scanner = self.scanners[scan_name]
        results = scanner.run(self.command_executor)
        self.prompt.add_hint(f"{scan_name.upper()} SCAN RESULTS\n\n{results['raw_output']}")
        return scanner.analyze(results)

    def auto_escalate(self):
        """Automated privilege escalation workflow"""
        # Run all scanners
        for name, scanner in self.scanners.items():
            scan_results = scanner.run(self.command_executor)

            # Add findings to hints
            analysis = scanner.analyze(scan_results)
            self.prompt.add_hint(f"{name.upper()} SCAN ANALYSIS\n\n{analysis}")
        
        # Continue with AI-powered escalation
        self.run()
    
    def run(self):
        self.running = True
        GlobalTimer.start()
        
        try:
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
                
                # Improved empty output detection
                cleaned_output = self._clean_output(output)
                print(f"[OUTPUT]\n{cleaned_output}")
                
                # Handle empty/meaningless output
                # import pdb; pdb.set_trace()  # Debugging line
                if self._is_empty_output(cleaned_output, command):
                    hint_msg = (
                        f"Command '{command}' returned empty output. "
                        f"Actual output was: {repr(output)}"
                    )
                    self.prompt.add_system_info(hint_msg)
                elif output == "password prompt":
                    self.prompt.add_system_info(
                        f"Command '{command}' requires a password. Please provide the password."
                    )
                else:
                    self.prompt.add_system_info(
                        f"Command '{command}' returned output:\n{cleaned_output}"
                    )
                
                self.prompt.add_command_history(command)
                
                self.prompt.last_command = command
                self.prompt.last_output = cleaned_output
                
                if RootDetector.got_root(self.hostname, cleaned_output):
                    print("\n[SUCCESS] Root access achieved!")
                    summary = self._generate_summary()
                    print(f"\n[SUMMARY]\n{summary}")
                    break
                    
                time.sleep(1)  # Rate limiting

        except Exception as e:
            debug_logger.error(f"Session error: {str(e)}")
            raise
        finally:
            GlobalTimer.stop("Privilege escalation session")
            self.running = False

    def _clean_output(self, output: str) -> str:
        """Remove shell prompts and whitespace artifacts"""
        if not output:
            return ""
        
        # First split into lines and strip each line
        lines = [line.strip() for line in output.splitlines()]
        
        # Filter out lines that are just shell prompts
        filtered_lines = []
        prompt_pattern = re.compile(
            r'^'                          # Start of line
            r'([\w-]+@[\w-]+:[~\w/]*\s*'  # user@host:path
            r'|\[\w+@\w+\s[\w/]+\]\s*'    # [user@host dir]
            r'|\$\s*'                     # Just $
            r'|#\s*'                      # Just #
            r')$'                         # End of line
        )
        
        for line in lines:
            if not prompt_pattern.fullmatch(line):
                filtered_lines.append(line)
        
        # Rejoin non-empty lines
        cleaned = '\n'.join(filtered_lines).strip()
        
        # Remove any remaining command echo
        if cleaned.startswith('$ ') or cleaned.startswith('# '):
            cleaned = cleaned[2:].strip()
        
        return cleaned

    def _is_empty_output(self, cleaned_output: str, command: str) -> bool:
        """Determine if output is effectively empty"""
        if not cleaned_output:
            return True
        
        # Check if output is just the command echo
        if cleaned_output.strip() == command.strip():
            return True
        
        # Check for common false positives
        false_positives = [
            'command not found',
            'permission denied',
            'no such file or directory'
        ]
        
        if any(fp in cleaned_output.lower() for fp in false_positives):
            return False
        
        # Final check for very short outputs that might be prompts
        if len(cleaned_output) < 20 and re.search(r'@|\[|\$|#', cleaned_output):
            return True
        
        return False
    
    def _generate_summary(self) -> str:
        summary = "\n[START OF SUMMARY]\n"
        summary = "Privilege Escalation Summary:\n\n"
        summary += "Commands executed:\n"
        for command in self.prompt.command_history:
            summary += f"- {command}\n"
        summary += "\nSystem information:\n"
        for info in self.prompt.system_info:
            summary += f"- {info}\n"
        summary += "\nKnown facts:\n"
        for fact in self.prompt.facts:
            summary += f"- {fact}\n"
        summary += "\nHints:\n"
        for hint in self.prompt.hints:
            summary += f"- {hint}\n"
        summary += "\nAvoid:\n"
        for avoid in self.prompt.avoids:
            summary += f"- {avoid}\n"
        summary += "\n\n[END OF SUMMARY]"
        return summary