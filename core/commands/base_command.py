from abc import ABC, abstractmethod

class BaseCommand(ABC):
    @abstractmethod
    def execute(self, command: str) -> str:
        pass
    
    @abstractmethod
    def upload_file(self, local_path: str, remote_path: str) -> bool:
        pass
    
    @abstractmethod
    def download_file(self, remote_path: str, local_path: str) -> bool:
        pass