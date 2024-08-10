from typing import List, Literal, Optional

from pydantic import BaseModel, Field

from db.models import ChatMessage


class ExecSignal(BaseModel):
    status: Literal["info", "warning", "error"]
    text: str
    varnames: Optional[List[str]] = Field(default=None)
    response: Optional[ChatMessage] = Field(default=None)
