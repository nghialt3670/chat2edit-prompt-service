from typing import Any, Dict, List, Optional, Union

from beanie import Document, Link, PydanticObjectId
from pydantic import BaseModel, Field

from models.phase import ChatPhase


class Context(BaseModel):
    file_id: PydanticObjectId = Field(...)
    alias_to_count: Dict[str, int] = Field(default_factory=dict)
    id_to_varnames: Dict[str, List[str]] = Field(default_factory=dict)


class Chat(Document):
    context: Context = Field(...)
    phases: List[Link["ChatPhase"]] = Field(default_factory=list)
