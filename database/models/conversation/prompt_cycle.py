from typing import Optional

from database.models.conversation.exec_message import ExecMessage
from pydantic import BaseModel


class PromptCycle(BaseModel):
    answer: Optional[str] = None
    exec_message: Optional[ExecMessage] = None
