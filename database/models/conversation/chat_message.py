from datetime import datetime
from typing import List
from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    text: str
    file_ids: List[str] = Field(default_factory=list)
    varnames: List[str] = Field(default_factory=list)
    timestamp: int = Field(default_factory=lambda: round(datetime.now().timestamp()))
