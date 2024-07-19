from datetime import datetime

from bson import ObjectId
from pydantic import BaseModel, Field


class Document(BaseModel):
    id: ObjectId = Field(default_factory=ObjectId, alias="_id")
    timestamp: int = Field(default_factory=lambda: round(datetime.now().timestamp()))

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: lambda v: str(v),
        }
