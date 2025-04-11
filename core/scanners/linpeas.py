import tempfile
import os
from ..commands.abstract_command import AbstractCommand
from ..scanners.abstract_scanner import AbstractScanner
from core.utils.logger import debug_logger
from typing import Dict, Any

class LinPEASScanner(AbstractScanner):
    def __init__(self):
        self.local_path = "external_tools/linpeas"
        self.remote_path = "/tmp"
        
    def run(self, command_executor: AbstractCommand) -> Dict[str, Any]:
        try:
            # Upload linPEAS
            command_executor.upload(
                f"{self.local_path}/linpeas.sh",
                f"{self.remote_path}/linpeas.sh"
            )
            
            # Make executable and run
            command_executor.execute(f"chmod +x {self.remote_path}")
            output = command_executor.execute(f"{self.remote_path} -a")
            
            return {
                'raw_output': output,
                'vulnerabilities': self._parse_output(output)
            }
        except Exception as e:
            debug_logger.error(f"linPEAS scan failed: {str(e)}")
            return {'error': str(e)}

    def _parse_output(self, output: str) -> list:
        # Parse linPEAS output for critical findings
        vulnerabilities = []
        current_section = None
        
        for line in output.split('\n'):
            if line.startswith('╔═'):
                current_section = line.strip('╔═╗ ')
            elif line.startswith('  [!]'):
                vulnerabilities.append({
                    'section': current_section,
                    'finding': line.strip()
                })
        
        return vulnerabilities

    def analyze(self, results: Dict[str, Any]) -> str:
        if 'error' in results:
            return f"linPEAS scan failed: {results['error']}"
        
        analysis = "linPEAS Scan Results:\n"
        for vuln in results.get('vulnerabilities', []):
            analysis += f"\n[!] {vuln['section']}\n"
            analysis += f"    {vuln['finding']}\n"
        
        return analysis