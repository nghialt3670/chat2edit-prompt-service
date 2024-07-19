from datetime import datetime
from typing import List

from bson import Timestamp
from pydantic import BaseModel, Field


class RequestMessage(BaseModel):
    text: str
    file_ids: List[str]
    timestamp: int = Field(default_factory=lambda: round(datetime.now().timestamp()))

