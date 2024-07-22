from core.schemas.fabric.fabric_object import FabricObject


class FabricRect(FabricObject):
    rx: int = 0
    ry: int = 0
    type: str = "Rect"
