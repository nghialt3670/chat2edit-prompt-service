from typing import Optional

from pydantic import BaseModel

from db.models.conversation.exec_message import ExecMessage


class PromptCycle(BaseModel):
    answer: Optional[str] = None
    exec_message: Optional[ExecMessage] = None
