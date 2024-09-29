from typing import Literal

from core.providers.fabric.models.fabric_object import FabricObject


class FabricRect(FabricObject):
    rx: int = 0
    ry: int = 0
    type: Literal["Rect"] = "Rect"
