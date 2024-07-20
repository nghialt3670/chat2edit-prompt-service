from typing import List, Optional

from pydantic import BaseModel, Field

from database.models.conversation.chat_message import ChatMessage
from database.models.conversation.prompt_cycle import PromptCycle


class ChatCycle(BaseModel):
    request: ChatMessage
    prompt_cycles: List[PromptCycle] = Field(default=list)
    response: Optional[ChatMessage] = Field(default=None)
