from typing import Dict, List
from pydantic import BaseModel, Field

from database.models.conversation.variable import Variable


class Context(BaseModel):
    variables: List[Variable] = Field(default=list)
    type_to_count: Dict[str, int] = Field(default=dict)
