from typing import List

from bson import ObjectId
from pydantic import Field

from database.models.conversation.chat_cycle import ChatCycle
from database.models.conversation.context import Context
from database.models.document import Document


class Conversation(Document):
    user_id: ObjectId
    title: str = Field(default="")
    context: Context = Field(default_factory=Context)
    chat_cycles: List[ChatCycle] = Field(default_factory=list)
