from typing import List, Optional

from db.models.conversation.chat_message import ChatMessage
from db.models.conversation.prompt_cycle import PromptCycle
from pydantic import BaseModel, Field


class ChatCycle(BaseModel):
    request: ChatMessage
    prompt_cycles: List[PromptCycle] = Field(default_factory=list)
    response: Optional[ChatMessage] = Field(default=None)
