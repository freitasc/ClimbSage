from abc import ABC, abstractmethod

class AbstractClient(ABC):
    @abstractmethod
    def get_response(self, system_prompt: str, user_prompt: str) -> str:
        pass

    @abstractmethod
    def filter_command(self, response: str) -> str:
        pass