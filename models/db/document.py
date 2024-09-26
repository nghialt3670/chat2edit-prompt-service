from datetime import datetime
from typing import Any

from bson import ObjectId
from pydantic import BaseModel, Field, field_validator

from utils.time import utc_now


class Document(BaseModel):
    id: ObjectId = Field(alias="_id", default_factory=ObjectId)
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)

    @field_validator("id", mode="before")
    def validate_id(cls, value) -> ObjectId:
        if isinstance(value, ObjectId):
            return value
        try:
            return ObjectId(value)
        except Exception:
            raise ValueError(f"Invalid ObjectId format: {value}")

    def __setattr__(self, name: str, value: Any) -> None:
        if name != "updated_at":
            super().__setattr__("updated_at", utc_now())
        super().__setattr__(name, value)

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
