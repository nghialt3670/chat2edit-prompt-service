from typing import List, Optional

from bson import ObjectId
from pydantic import BaseModel, Field

from schemas.attachment_schema import AttachmentSchema
from schemas.object_id_schema import ObjectIdSchema


class MessageSchema(BaseModel):
    chat_id: Optional[ObjectIdSchema] = Field(default=None)
    text: str = Field(...)
    attachments: List[AttachmentSchema] = Field(default_factory=list)

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
