from pydantic import BaseModel

from database.models.conv.exec_message import ExecMessage


class PromptCycle(BaseModel):
    answer: str
    exec_message: ExecMessage
