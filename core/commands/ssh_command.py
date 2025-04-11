from pwn import *
from .base_command import BaseCommand
from core.utils.logger import debug_logger
import time
from core.utils.cleaner import clean_output

class SSHCommand(BaseCommand):
    def __init__(self, host: str, port: int, username: str, password: str):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.conn = None
        self.shell = None
        self.prompt = b'$'  # Default prompt
        self.connect()

    def _wait_for_prompt(self, timeout=5):
        """Wait until we see the shell prompt"""
        start_time = time.time()
        output = b''
        
        while time.time() - start_time < timeout:
            try:
                data = self.shell.recv(timeout=0.5)
                if not data:
                    continue
                
                output += data
                if self.prompt in output:
                    # Return everything before the prompt
                    return output.split(self.prompt)[0].decode('utf-8').strip()
                    
            except EOFError:
                debug_logger.error("Shell connection closed unexpectedly")
                self.connect()  # Reconnect
                return ""
            except Exception as e:
                debug_logger.error(f"Error receiving data: {str(e)}")
                continue
                
        debug_logger.warning(f"Prompt not found in output: {output}")
        return output.decode('utf-8').strip()

    def connect(self):
        try:
            if self.conn:
                self.conn.close()
                
            self.conn = ssh(
                user=self.username,
                host=self.host,
                port=self.port,
                password=self.password
            )
            shell_output = self.conn.run('echo $SHELL').recvall()
            self.shell = self.conn.process('/bin/bash' if b'bash' in shell_output else '/bin/sh')

            
            # Detect prompt by sending empty command
            self.shell.sendline(b'echo "CLIMBSAGE_PROMPT:$PWD# "')
            prompt_detection = self._wait_for_prompt()
            if prompt_detection:
                self.prompt = prompt_detection.splitlines()[-1].encode() + b' '
            else:
                self.prompt = b'$ '  # Fallback
            
            debug_logger.debug(f"SSH connection established with prompt: {self.prompt}")
            
        except Exception as e:
            debug_logger.error(f"SSH connection failed: {str(e)}")
            raise

    def execute(self, command: str) -> str:
        if not self.shell:
            self.connect()

        try:
            # Clear any existing output
            while self.shell.recv(timeout=0.1):
                pass
                
            # Send command as bytes
            self.shell.sendline(command.encode())
            debug_logger.debug(f"Command sent: {command}")
            
            # Get output
            output = self._wait_for_prompt()
            
            # Handle sudo password prompts
            if "password for " + self.username in output:
                self.shell.sendline(self.password.encode())
                output += "\n" + self._wait_for_prompt()
                
            output = clean_output(output)
            debug_logger.debug(f"Command output: {output[:200]}...")  # Log first 200 chars
            return output
            
        except Exception as e:
            debug_logger.error(f"Command execution failed: {str(e)}")
            self.connect()  # Attempt to reconnect
            raise

    def upload_file(self, local_path: str, remote_path: str) -> bool:
        try:
            with open(local_path, 'rb') as f:
                data = f.read()
            self.conn.upload_data(data, remote_path)
            return True
        except Exception as e:
            debug_logger.error(f"File upload failed: {str(e)}")
            return False

    def download_file(self, remote_path: str, local_path: str) -> bool:
        try:
            data = self.conn.download_data(remote_path)
            with open(local_path, 'wb') as f:
                f.write(data)
            return True
        except Exception as e:
            debug_logger.error(f"File download failed: {str(e)}")
            return False

    def __del__(self):
        if self.shell:
            self.shell.close()
        if self.conn:
            self.conn.close()