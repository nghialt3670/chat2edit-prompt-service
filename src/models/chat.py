from typing import Dict, List

from beanie import Document, Link, PydanticObjectId
from pydantic import BaseModel, Field

from models.phase import ChatPhase


class ChatState(BaseModel):
    context_id: PydanticObjectId = Field(...)
    alias_to_count: Dict[str, int] = Field(default_factory=dict)
    id_to_varnames: Dict[str, List[str]] = Field(default_factory=dict)


class Chat(Document):
    state: ChatState = Field(...)
    phases: List[Link["ChatPhase"]] = Field(default_factory=list)

    class Settings:
        name = "internal-chats"
