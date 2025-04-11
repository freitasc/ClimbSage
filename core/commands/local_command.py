import subprocess
from .abstract_command import AbstractCommand
from core.utils.logger import debug_logger

class LocalCommand(AbstractCommand):
    def __init__(self):
        debug_logger.debug("Local command executor initialized")

    def execute(self, command: str) -> str:
        try:
            result = subprocess.run(
                command,
                shell=True,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            debug_logger.debug(f"Local command executed: {command}")
            return result.stdout
        except subprocess.CalledProcessError as e:
            debug_logger.error(f"Command failed: {command}\nError: {e.stderr}")
            return e.stderr
        except Exception as e:
            debug_logger.error(f"Unexpected error executing command: {str(e)}")
            return str(e)

    def upload_file(self, local_path: str, remote_path: str) -> bool:
        """For local execution, this just copies files"""
        import shutil
        try:
            shutil.copy(local_path, remote_path)
            debug_logger.debug(f"Copied {local_path} to {remote_path}")
            return True
        except Exception as e:
            debug_logger.error(f"File copy failed: {str(e)}")
            return False

    def download_file(self, remote_path: str, local_path: str) -> bool:
        """For local execution, this just copies files"""
        return self.upload_file(remote_path, local_path)