from typing import List, Literal

from pydantic import BaseModel


class ExecMessage(BaseModel):
    status: Literal["info", "warning", "error"]
    text: str
    commands: List[str]
