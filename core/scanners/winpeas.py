import tempfile
import os
from ..commands.abstract_command import AbstractCommand
from ..scanners.abstract_scanner import AbstractScanner
from core.utils.logger import debug_logger
from typing import Dict, Any

class WinPEASScanner(AbstractScanner):
    def __init__(self):
        self.local_path = "external_tools/Windows/winpeas"
        self.remote_path = "C:\\Windows\\Temp"
        
    def run(self, command_executor: AbstractCommand) -> Dict[str, Any]:
        try:
            # Upload WinPEAS
            command_executor.upload(
                f"{self.local_path}/winpeas.exe",
                f"{self.remote_path}\\winpeas.exe"
            )
            
            # Run WinPEAS (no need for chmod on Windows)
            output = command_executor.execute(f"{self.remote_path}\\winpeas.exe quiet")
            
            return {
                'raw_output': output,
                'vulnerabilities': self._parse_output(output)
            }
        except Exception as e:
            debug_logger.error(f"WinPEAS scan failed: {str(e)}")
            return {'error': str(e)}

    def _parse_output(self, output: str) -> list:
        # Parse WinPEAS output for critical findings
        vulnerabilities = []
        current_section = None
        
        for line in output.split('\n'):
            line = line.strip()
            if line.startswith('===') and '===' in line[3:]:
                current_section = line.strip('= ').strip()
            elif '(!)' in line or '(i)' in line or '(?)' in line:
                vulnerabilities.append({
                    'section': current_section,
                    'finding': line
                })
            elif line.startswith('[*]') or line.startswith('[!]'):
                vulnerabilities.append({
                    'section': current_section,
                    'finding': line
                })
        
        return vulnerabilities

    def analyze(self, results: Dict[str, Any]) -> str:
        if 'error' in results:
            return f"WinPEAS scan failed: {results['error']}"
        
        analysis = "WinPEAS Scan Results:\n"
        for vuln in results.get('vulnerabilities', []):
            analysis += f"\n[!] {vuln['section']}\n"
            analysis += f"    {vuln['finding']}\n"
        
        return analysis