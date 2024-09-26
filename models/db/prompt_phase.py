from typing import List, Optional

from pydantic import BaseModel, Field

from models.db.execution import Execution


class PromptPhase(BaseModel):
    responses: Optional[List[str]] = Field(default_factory=list)
    durations: Optional[List[int]] = Field(default_factory=list)
    tracebacks: Optional[List[str]] = Field(default_factory=list)
    execution: Optional[Execution] = Field(default=None)
