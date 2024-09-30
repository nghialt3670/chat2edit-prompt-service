from beanie import PydanticObjectId
from pydantic import BaseModel, Field


class ChatCreateRequest(BaseModel):
    chat_id: PydanticObjectId = Field(...)