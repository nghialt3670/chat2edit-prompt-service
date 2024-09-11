from typing import Literal
from core.schemas.fabric.fabric_object import FabricObject


class FabricRect(FabricObject):
    rx: int = 0
    ry: int = 0
    type: Literal["Rect"] = "Rect"
    
    is_prompt: bool = False
