import subprocess
import os
import re
import time
from typing import Dict, Any
from .abstract_command import AbstractCommand
from core.utils.logger import debug_logger
from core.utils.cleaner import clean_output

class LocalCommand(AbstractCommand):
    def __init__(self):
        self.shell = os.getenv('SHELL', '/bin/bash')
        self.prompt = self._detect_prompt()
        debug_logger.debug(f"Local command executor initialized with shell: {self.shell}")

    def _detect_prompt(self) -> str:
        """Detect the current shell's prompt"""
        try:
            # Get PS1 variable or fallback to basic prompt
            result = subprocess.run(
                ['echo', '$PS1'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                shell=True
            )
            ps1 = result.stdout.strip() or '$ '
            return re.sub(r'\\[a-zA-Z]', '', ps1)  # Remove escape sequences
        except Exception:
            return '$ '

    def _wait_for_process(self, process, timeout: int = 300) -> str:
        """Wait for process completion with timeout"""
        output = []
        start_time = time.time()
        
        while True:
            # Check for timeout
            if time.time() - start_time > timeout:
                process.kill()
                raise TimeoutError(f"Process timed out after {timeout} seconds")
            
            # Read available output
            line = process.stdout.readline()
            if not line:
                if process.poll() is not None:
                    break  # Process completed
                time.sleep(0.1)
                continue
                
            decoded = line.strip()
            output.append(decoded)
            debug_logger.debug(f"Process output: {decoded}")
            
        return '\n'.join(output)

    def execute(self, command: str, timeout: int = 300) -> str:
        """Execute a command locally and return cleaned output"""
        try:
            debug_logger.debug(f"Executing local command: {command}")
            
            process = subprocess.Popen(
                command,
                shell=True,
                executable=self.shell,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            output = self._wait_for_process(process, timeout)
            cleaned = clean_output(output)
            
            debug_logger.debug(f"Command completed with return code: {process.returncode}")
            return cleaned
            
        except Exception as e:
            debug_logger.error(f"Local command failed: {str(e)}")
            raise

    def upload(self, local_path: str, remote_path: str) -> bool:
        """Local version just copies files"""
        try:
            import shutil
            debug_logger.debug(f"Copying {local_path} to {remote_path}")
            # copy directory or file
            if os.path.isdir(local_path):
                shutil.copytree(local_path, f"{remote_path}"+"/"+os.path.basename(local_path))
            else:
                shutil.copy2(local_path, remote_path)

            return True
        except Exception as e:
            debug_logger.error(f"Local upload failed: {str(e)}")
            return False

    def download_file(self, remote_path: str, local_path: str) -> bool:
        """Local version just copies files"""
        return self.upload(remote_path, local_path)

    def __del__(self):
        # Cleanup if needed
        pass