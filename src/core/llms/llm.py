from abc import ABC, abstractmethod
from typing import Iterable


class LLM(ABC):
    @abstractmethod
    async def __call__(self, messages: Iterable[str]) -> str:
        pass
