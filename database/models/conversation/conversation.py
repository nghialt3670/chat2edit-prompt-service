from typing import Dict, List

from bson import ObjectId
from database.models.conversation.chat_cycle import ChatCycle
from database.models.document import Document
from pydantic import Field


class Conversationersation(Document):
    user_id: ObjectId
    context_id: ObjectId
    title: str = Field(default="")
    alias_to_count: Dict[str, int] = Field(default_factory=dict)
    chat_cycles: List[ChatCycle] = Field(default_factory=list)
