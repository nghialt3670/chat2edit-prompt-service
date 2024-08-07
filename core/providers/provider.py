from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Literal, Optional

from core.providers.exec_signal import ExecSignal
from db.models import ChatMessage

DEFAULT_SIGNAL = ExecSignal(status="info", text="Commands executed successfully.")


class Provider(ABC):
    def __init__(self) -> None:
        self._signal = DEFAULT_SIGNAL
        self._context = {}

    @abstractmethod
    def get_functions(self) -> List[Callable]:
        pass

    @abstractmethod
    def get_exemplars(self) -> str:
        pass

    def get_signal(self) -> ExecSignal:
        return self._signal

    def get_context(self) -> Dict[str, Any]:
        return self._context

    def clear_signal(self) -> None:
        self._signal = DEFAULT_SIGNAL

    def set_context(self, context: Dict[str, Any]) -> None:
        self._context = context

    def _set_signal(
        self,
        status: Literal["info", "warning", "error"],
        text: str = "",
        varnames: Optional[List[str]] = None,
        response: Optional[ChatMessage] = None,
    ) -> None:
        self._signal = ExecSignal(status=status, text=text)
        self._signal.varnames = varnames
        self._signal.response = response
