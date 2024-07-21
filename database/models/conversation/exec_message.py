from typing import List, Literal, Optional

from database.models.conversation.chat_message import ChatMessage
from pydantic import BaseModel, Field


class ExecMessage(BaseModel):
    status: Literal["info", "warning", "error"]
    commands: List[str]
    text: str
    varnames: Optional[List[str]] = Field(default=None)
    response: Optional[ChatMessage] = Field(default=None)
