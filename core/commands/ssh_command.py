from pwn import *
from .base_command import BaseCommand
from core.utils.logger import debug_logger

class SSHCommand(BaseCommand):
    def __init__(self, host: str, port: int, username: str, password: str):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.conn = None
        self.shell = None
        self.connect()
    
    def connect(self):
        try:
            self.conn = ssh(
                user=self.username,
                host=self.host,
                port=self.port,
                password=self.password
            )
            self.shell = self.conn.process('/bin/sh', env={'TERM': ''})
            debug_logger.debug("SSH connection established")
        except Exception as e:
            debug_logger.error(f"SSH connection failed: {str(e)}")
            raise
    
    def execute(self, command: str) -> str:
        if not self.shell:
            self.connect()
        
        self.shell.sendline(command)
        output = self.shell.recvuntil('$ ').decode('utf-8').strip()
        return output
    
    def upload_file(self, local_path: str, remote_path: str) -> bool:
        try:
            self.conn.upload(local_path, remote_path)
            return True
        except Exception as e:
            debug_logger.error(f"File upload failed: {str(e)}")
            return False
    
    def download_file(self, remote_path: str, local_path: str) -> bool:
        try:
            self.conn.download(remote_path, local_path)
            return True
        except Exception as e:
            debug_logger.error(f"File download failed: {str(e)}")
            return False
    
    def __del__(self):
        if self.shell:
            self.shell.close()
        if self.conn:
            self.conn.close()