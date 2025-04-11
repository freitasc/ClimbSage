from abc import ABC, abstractmethod
from typing import Dict, Any

class AbstractScanner(ABC):
    @abstractmethod
    def run(self, command_executor) -> Dict[str, Any]:
        pass

    @abstractmethod
    def analyze(self, results: Dict[str, Any]) -> str:
        pass