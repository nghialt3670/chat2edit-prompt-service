from typing import List, Literal, Optional

from pydantic import BaseModel, Field

from models.db.context_message import ContextMessage


class Execution(BaseModel):
    commands: List[str] = Field(default_factory=list)
    durations: Optional[List[int]] = Field(default_factory=list)
    traceback: Optional[str] = Field(default=None)
    feedback: Optional[ContextMessage] = Field(default=None)
    response: Optional[ContextMessage] = Field(default=None)
