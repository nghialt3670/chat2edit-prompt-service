from typing import List, Literal, Optional

from pydantic import BaseModel, Field

from db.models.conversation.chat_message import ChatMessage


class ExecMessage(BaseModel):
    status: Literal["info", "warning", "error"]
    commands: List[str]
    text: str
    varnames: Optional[List[str]] = Field(default=None)
    response: Optional[ChatMessage] = Field(default=None)
