from typing import Literal

from pydantic import Field

from core.providers.fabric.models.fabric_object import FabricObject


class FabricRect(FabricObject):
    type: Literal["Rect"] = Field(default="Rect")
    rx: int = Field(default=0)
    ry: int = Field(default=0)
    is_query: bool = Field(default=False)
