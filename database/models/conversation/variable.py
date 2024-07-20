from typing import Any, Literal, Optional
from pydantic import BaseModel


class Variable(BaseModel):
    type: Literal["file", "object", "primitive", "list"]
    class_name: Optional[str] = None
    name: str
    value: Any
