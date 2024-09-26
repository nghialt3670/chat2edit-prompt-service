from typing import List, Optional

from bson import ObjectId
from pydantic import Field

from models.db.context_message import ContextMessage
from models.db.document import Document
from models.db.prompt_phase import PromptPhase


class ChatPhase(Document):
    chat_id: ObjectId = Field(default_factory=ObjectId)
    request: ContextMessage = Field(...)
    prompt_phases: List[PromptPhase] = Field(default_factory=list)
    response: Optional[ContextMessage] = Field(default=None)
