from pydantic import BaseModel, Field


class File(BaseModel):
    buffer: bytes = Field(repr=False)
    name: str = Field(...)
    content_type: str = Field(...)
