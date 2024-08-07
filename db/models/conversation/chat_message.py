from datetime import datetime
from typing import List

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    text: str
    varnames: List[str] = Field(default_factory=list)
