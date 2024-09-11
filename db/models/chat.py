from typing import Any, Dict, List

from bson import ObjectId
from pydantic import Field, validator

from db.models.chat_cycle import ChatCycle
from db.models.document import Document


class Chat(Document):
    context_id: ObjectId
    alias_to_count: Dict[str, int] = Field(default_factory=dict)
    chat_cycles: List[ChatCycle] = Field(default_factory=list)
    id_to_varname: Dict[str, str] = Field(default_factory=dict)

    @validator("context_id", pre=True, always=True)
    def parse_object_id(cls, value: Any) -> ObjectId:
        try:
            return ObjectId(value)
        except Exception:
            raise ValueError(f"Invalid ObjectId format: {value}")
