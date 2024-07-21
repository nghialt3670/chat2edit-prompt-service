from bson import ObjectId
from database.models.document import Document
from database.models.user.settings import Settings
from pydantic import BaseModel, Field


class User(Document):
    clerk_user_id: str
    settings: Settings = Field(default_factory=Settings)
