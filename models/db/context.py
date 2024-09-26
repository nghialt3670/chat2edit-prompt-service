from typing import Any, Dict, List, Optional, Union

from bson import ObjectId
from pydantic import BaseModel, Field

from models.db.document import Document


class Context(Document):
    file_id: ObjectId = Field(...)
    data: Optional[Union[bytes, Dict[str, Any]]] = Field(default=None)
    alias_to_count: Dict[str, int] = Field(default_factory=dict)
    id_to_varnames: Dict[str, List[str]] = Field(default_factory=dict)
