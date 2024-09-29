from typing import Any, List, Literal, Optional, Tuple
from uuid import uuid4

from pydantic import BaseModel, Field


class FabricObject(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    type: str = "FabricObject"
    version: str = "6.0.1"
    originX: str = "left"
    originY: str = "top"
    left: float = 0.0
    top: float = 0.0
    width: Optional[float] = None
    height: Optional[float] = None
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

    is_prompt: bool = False

    def get_box(self) -> Tuple[int, int, int, int]:
        return (
            round(self.left),
            round(self.top),
            round(self.left + self.width),
            round(self.top + self.height),
        )

    def rotate(self, angle: int) -> None:
        self.angle += angle

    def flip(self, axis: Literal["x", "y"]) -> None:
        if axis == "x":
            self.flipX = not self.flipX
        elif axis == "y":
            self.flipY = not self.flipY
        else:
            raise ValueError("Invalid argument for axis")

    def is_size_initialized(self) -> bool:
        return self.width and self.height

    def __hash__(self) -> int:
        return hash(self.id)

    def __eq__(self, value: object) -> bool:
        return isinstance(value, FabricObject) and value.id == self.id
