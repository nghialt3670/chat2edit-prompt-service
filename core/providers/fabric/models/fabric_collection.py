from typing import List, Union

from pydantic import BaseModel, Field

from core.providers.fabric.models.fabric_object import FabricObject


class FabricCollection(BaseModel):
    objects: List[FabricObject] = Field(default_factory=list)
