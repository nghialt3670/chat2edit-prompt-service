from bson import ObjectId
from pydantic import Field

from models.db.context import Context
from models.db.document import Document
from models.db.settings import Settings


class Chat(Document):
    account_id: ObjectId = Field(...)
    context_id: ObjectId = Field(...)
    settings: Settings = Field(...)
    title: str = Field(default="")
