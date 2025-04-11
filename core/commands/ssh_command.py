from pwn import *
from .abstract_command import AbstractCommand
from core.utils.logger import debug_logger
import time
from core.utils.cleaner import clean_output

class SSHCommand(AbstractCommand):
    def __init__(self, host: str, port: int, username: str, password: str):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.conn = None
        self.shell = None
        self.prompt = b'$'  # Default prompt
        self.connect()

    def _wait_for_prompt(self, timeout=300):
        """Universal prompt waiting that works for all shells and long commands"""
        output = b''
        active = False  # Track if we're seeing active command output
        last_data_time = time.time()
        
        while True:
            try:
                # Check overall timeout
                if time.time() - last_data_time > timeout:
                    debug_logger.warning(f"Timeout after {timeout}s of inactivity")
                    break
                
                # Receive data with short timeout
                data = self.shell.recv(timeout=0.5)
                if not data:
                    if active:  # Only log if we had output before
                        debug_logger.debug("No data received, waiting...")
                    continue
                
                # Check if last command output was a 
                    
                output += data
                last_data_time = time.time()
                active = True
                
                # Check for common shell prompts (universal detection)
                prompt_patterns = [
                    rb'\$ $',          # bash/zsh
                    rb'# $',            # root shell
                    rb'>>> ',           # Python
                    rb'In \[\d+\]: ',   # IPython
                    rb'\? $'            # csh/tcsh
                ]
                
                
                # Check if we have a complete command output
                if any(re.search(pattern, output) for pattern in prompt_patterns):
                    # Extract everything before the prompt
                    for pattern in prompt_patterns:
                        if re.search(pattern, output):
                            parts = re.split(pattern, output)
                            if len(parts) > 1:
                                return parts[0].decode('utf-8', errors='ignore').strip()
                    
                    # Fallback if split failed
                    return output.decode('utf-8', errors='ignore').strip()
                
                # Check for password prompts
                password_patterns = [
                    b'[Pp]assword:', 
                    b'[Pp]assphrase:',
                    b'Enter [Pp]assword'
                ]
                
                if any(re.search(pattern, output) for pattern in password_patterns):
                    # If we detect a password prompt, send the password
                    debug_logger.debug("Detected password prompt")
                    return 'password prompt'
                    
            except EOFError:
                debug_logger.error("Shell connection terminated")
                self.connect()
                return output.decode('utf-8', errors='ignore').strip()
            except Exception as e:
                debug_logger.error(f"Receive error: {str(e)}")
                continue
        
        return output.decode('utf-8', errors='ignore').strip()

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
                
            output = clean_output(output)
            debug_logger.debug(f"Command output: {output[:200]}...")  # Log first 200 chars
            return output
            
        except Exception as e:
            debug_logger.error(f"Command execution failed: {str(e)}")
            self.connect()  # Attempt to reconnect
            raise
    
    def upload(self, local_path: str, remote_path: str) -> bool:
        try:
            self.conn.upload(local_path, remote_path)
            return True
        except Exception as e:
            debug_logger.error(f"Upload failed: {str(e)}")
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