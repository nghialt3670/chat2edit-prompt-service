from datetime import datetime
from bson import ObjectId
from pydantic import BaseModel, Field

from schemas.object_id_schema import ObjectIdSchema


class ChatSchema(BaseModel):
    id: ObjectIdSchema = Field(...)
    title: str = Field(...)
    updated_at: datetime = Field(...)

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
