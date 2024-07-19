from datetime import datetime
from typing import List, Literal

from bson import Timestamp
from pydantic import BaseModel, Field


class ResponseMessage(BaseModel):
    status: Literal["sucess", "error"]
    text: str
    file_ids: List[str]
    timestamp: int = Field(default_factory=lambda: round(datetime.now().timestamp()))
