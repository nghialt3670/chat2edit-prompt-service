from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field

from database.models.conversation.chat_message import ChatMessage


class ExecSignal(BaseModel):
    status: Literal["info", "warning", "error"]
    text: str
    varnames: Optional[List[str]] = Field(default=None)
    response: Optional[ChatMessage] = Field(default=None)
