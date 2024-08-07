from typing import Any, Dict, List

from bson import ObjectId
from db.models.conversation.chat_cycle import ChatCycle
from db.models.document import Document
from pydantic import Field, validator


class Conversation(Document):
    context_id: ObjectId
    alias_to_count: Dict[str, int] = Field(default_factory=dict)
    chat_cycles: List[ChatCycle] = Field(default_factory=list)

    @validator('context_id', pre=True, always=True)
    def parse_object_id(cls, value: Any) -> ObjectId:
        try:
            return ObjectId(value)
        except Exception:
            raise ValueError(f"Invalid ObjectId format: {value}")