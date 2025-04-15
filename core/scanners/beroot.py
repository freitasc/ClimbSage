import tempfile
import os
from ..commands.abstract_command import AbstractCommand
from ..scanners.abstract_scanner import AbstractScanner
from core.utils.logger import debug_logger
from typing import Dict, Any

class BeRootScanner(AbstractScanner):
    def __init__(self):
        self.local_path = 'external_tools/Linux/BeRoot'
        self.remote_path = '/tmp'
        
    def run(self, command_executor: AbstractCommand) -> Dict[str, Any]:
        try:
            # Upload BeRoot
            command_executor.upload(f"{self.local_path}", self.remote_path)
            
            # Run BeRoot
            command = f"python3 {self.remote_path}/BeRoot/beroot.py 2>/dev/null"
            output = command_executor.execute(command)
            
            return {
                'raw_output': output,
                'vulnerabilities': self._parse_output(output)
            }
        except Exception as e:
            debug_logger.error(f"BeRoot scan failed: {str(e)}")
            return {'error': str(e)}

    def _parse_output(self, output: str) -> list:
        # Parse BeRoot output to extract vulnerabilities
        vulnerabilities = []
        current_vuln = {}
        
        for line in output.split('\n'):
            if line.startswith('[+]'):
                if current_vuln:  # Save previous vulnerability
                    vulnerabilities.append(current_vuln)
                current_vuln = {
                    'type': line.split(']')[1].strip(),
                    'details': []
                }
            elif line.strip() and current_vuln:
                current_vuln['details'].append(line.strip())
        
        if current_vuln:
            vulnerabilities.append(current_vuln)
            
        return vulnerabilities

    def analyze(self, results: Dict[str, Any]) -> str:
        if 'error' in results:
            return f"BeRoot scan failed: {results['error']}"
        
        analysis = "BeRoot Scan Results:\n"
        for vuln in results.get('vulnerabilities', []):
            analysis += f"\n[!] {vuln['type']}\n"
            analysis += "\n".join(f"    {detail}" for detail in vuln['details'])
            analysis += "\n"
        
        return analysis