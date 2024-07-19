from abc import ABC, abstractmethod
from typing import Any, Callable, Iterable, List, Literal, Optional

from chat2edit.models.attachment import Attachment
from chat2edit.models.chat_cycle import ChatCycle
from chat2edit.models.chat_message import ChatMessage
from chat2edit.models.exec_signal import ExecSignal


class Provider(ABC):
    def __init__(self) -> None:
        self._signal = None

    @abstractmethod
    def get_functions(self) -> List[Callable[..., Any]]:
        pass

    @abstractmethod
    def get_exemplars(self) -> Iterable[Iterable[ChatCycle]]:
        pass

    def get_signal(self) -> Optional[ExecSignal]:
        return self._signal

    def clear_signal(self) -> None:
        self._signal = None

    def _set_signal(
        self,
        status: Literal["info", "warning", "error"],
        text: Optional[str] = None,
        attachments: Optional[List[Attachment]] = None,
        response: Optional[ChatMessage] = None,
    ) -> None:
        self._signal = ExecSignal(status)
        self._signal.text = text or self._signal.text
        self._signal.attachments = attachments or self._signal.attachments
        self._signal.response = response or self._signal.response

    def _info(
        self,
        text: str,
        attachments: Optional[List[Attachment]] = None,
    ) -> None:
        self._set_signal("info", text, attachments)

    def _warning(
        self,
        text: str,
        attachments: Optional[List[Attachment]] = None,
    ) -> None:
        self._set_signal("warning", text, attachments)

    def _error(
        self,
        text: str,
        attachments: Optional[List[Attachment]] = None,
    ) -> None:
        self._set_signal("error", text, attachments)

    def _reponse(self, response: ChatMessage) -> None:
        self._set_signal("info", response=response)
