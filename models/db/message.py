from typing import List, Optional

from bson import ObjectId
from pydantic import Field, field_validator

from models.db.document import Document


class Message(Document):
    chat_id: ObjectId = Field(...)
    text: str = Field(...)
    attachment_ids: List[ObjectId] = Field(default_factory=list)

    @field_validator("attachment_ids", mode="before")
    def validate_attachment_ids(cls, value) -> Optional[List[ObjectId]]:
        if value is None:
            return value

        if not isinstance(value, list):
            raise ValueError(
                f"Expected a list for 'attachment_ids', but got {type(value)}"
            )

        object_ids = []
        for item in value:
            if isinstance(item, ObjectId):
                object_ids.append(item)
            else:
                try:
                    object_ids.append(ObjectId(item))
                except Exception:
                    raise ValueError(f"Invalid ObjectId format: {item}")

        return object_ids
