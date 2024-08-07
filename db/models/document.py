from typing import Any
from bson import ObjectId
from pydantic import BaseModel, Field, validator


class Document(BaseModel):
    id: ObjectId = Field(default_factory=ObjectId, alias="_id")

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: lambda v: str(v),
        }
        
    @validator('id', pre=True, always=True)
    def parse_object_id(cls, value: Any) -> ObjectId:
        try:
            return ObjectId(value)
        except Exception:
            raise ValueError(f"Invalid ObjectId format: {value}")