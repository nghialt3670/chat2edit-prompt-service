from typing import List, Literal, Optional

from pydantic import BaseModel, Field


class ContextMessage(BaseModel):
    src: Literal["user", "system", "llm"]
    type: Literal["request", "response", "info", "warning", "error"]
    text: str = Field(min_length=1, max_length=500)
    varnames: List[str] = Field(default_factory=list)
