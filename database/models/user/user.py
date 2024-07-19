from bson import ObjectId
from pydantic import BaseModel, Field

from database.models.document import Document
from database.models.user.settings import Settings


class User(Document):
    clerk_user_id: str
    settings: Settings = Field(default_factory=Settings)
