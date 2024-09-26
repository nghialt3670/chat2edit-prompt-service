from typing import Literal, Optional

from bson import ObjectId
from pydantic import BaseModel, Field, field_validator, model_validator

from schemas.object_id_schema import ObjectIdSchema


class ThumbnailSchema(BaseModel):
    width: int = Field(...)
    height: int = Field(...)


class FileSchema(BaseModel):
    name: str = Field(...)
    content_type: str = Field(...)
    thumbnail: Optional[ThumbnailSchema] = Field(default=None)


class AttachmentSchema(BaseModel):
    id: ObjectIdSchema = Field(...)
    type: Literal["file", "link", "ref"]
    file: Optional[FileSchema] = Field(default=None)
    link: Optional[str] = Field(default=None)
    ref: Optional[ObjectIdSchema] = Field(default=None)

    @field_validator("id", "ref", mode="before")
    def validate_id(cls, value) -> ObjectId:
        if isinstance(value, ObjectId):
            return value
        try:
            return ObjectId(value)
        except Exception:
            raise ValueError(f"Invalid ObjectId format: {value}")

    @model_validator(mode="after")
    def validate(cls, obj):
        type_value = getattr(obj, "type")
        file_value = getattr(obj, "file")
        link_value = getattr(obj, "link")
        ref_value = getattr(obj, "ref")
        if type_value == "file" and file_value is None:
            raise ValueError("The 'file' field must be provided when type is 'file'")
        if type_value == "link" and link_value is None:
            raise ValueError("The 'link' field must be provided when type is 'link'")
        if type_value == "ref" and ref_value is None:
            raise ValueError("The 'ref' field must be provided when type is 'ref'")
        return obj

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
