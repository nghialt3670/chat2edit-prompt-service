from typing import Any, List, Optional
from uuid import uuid4

from pydantic import BaseModel, Field


class FabricObject(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    type: str = "FabricObject"
    version: str = "6.0.1"
    originX: str = "left"
    originY: str = "top"
    left: int = 0
    top: int = 0
    width: Optional[int] = None
    height: Optional[int] = None
    fill: str = "rgb(0,0,0)"
    selectable: Optional[bool] = True
    stroke: Optional[str] = None
    strokeWidth: int = 1
    strokeDashArray: Optional[List[int]] = None
    strokeLineCap: str = "butt"
    strokeDashOffset: int = 0
    strokeLineJoin: str = "miter"
    strokeUniform: bool = False
    strokeMiterLimit: int = 4
    scaleX: float = 1.0
    scaleY: float = 1.0
    angle: int = 0
    flipX: bool = False
    flipY: bool = False
    opacity: float = 1.0
    shadow: Optional[str] = None
    visible: bool = True
    backgroundColor: str = ""
    fillRule: str = "nonzero"
    paintFirst: str = "fill"
    globalCompositeOperation: str = "source-over"
    skewX: int = 0
    skewY: int = 0

    def is_size_initialized(self) -> bool:
        return self.width and self.height

    def __hash__(self) -> int:
        return hash(self.id)

    def __eq__(self, value: object) -> bool:
        return isinstance(value, FabricObject) and value.id == self.id