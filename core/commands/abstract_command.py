from abc import ABC, abstractmethod

class AbstractCommand(ABC):
    @abstractmethod
    def execute(self, command: str) -> str:
        pass
    
    @abstractmethod
    def upload(self, local_path: str, remote_path: str) -> bool:
        pass
    
    @abstractmethod
    def download_file(self, remote_path: str, local_path: str) -> bool:
        pass