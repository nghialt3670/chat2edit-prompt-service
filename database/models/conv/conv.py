from datetime import datetime
from typing import Any, Dict, List
from uuid import uuid4

from bson import ObjectId, Timestamp
from pydantic import BaseModel, Field

from database.models.conv.chat_cycle import ChatCycle
from database.models.document import Document


class Conv(Document):
    title: str = Field(default="")
    user_id: ObjectId
    context: Dict[str, Any] = Field(default_factory=dict)
    chat_cycles: List[ChatCycle] = Field(default_factory=list)
