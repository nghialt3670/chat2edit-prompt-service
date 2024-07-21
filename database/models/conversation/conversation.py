from typing import Dict, List

from bson import ObjectId
from pydantic import Field

from database.models.conversation.chat_cycle import ChatCycle
from database.models.document import Document


class Conversation(Document):
    user_id: ObjectId
    context_id: ObjectId
    title: str = Field(default="")
    alias_to_count: Dict[str, int] = Field(default_factory=dict)
    chat_cycles: List[ChatCycle] = Field(default_factory=list)
