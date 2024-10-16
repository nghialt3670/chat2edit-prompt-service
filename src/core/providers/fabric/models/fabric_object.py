from typing import List, Literal, Optional, Tuple
from uuid import uuid4

from pydantic import BaseModel, Field


class FabricObject(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    type: str = Field(default="FabricObject")
    originX: str = Field(default="left")
    originY: str = Field(default="top")
    left: float = Field(default=0.0)
    top: float = Field(default=0.0)
    width: float = Field(default=0.0)
    height: float = Field(default=0.0)
    fill: str = Field(default="rgb(0,0,0)")
    selectable: bool = Field(default=True)
    stroke: Optional[str] = Field(default=None)
    strokeWidth: int = Field(default=1)
    strokeDashArray: Optional[List[int]] = Field(default=None)
    strokeLineCap: str = Field(default="butt")
    strokeDashOffset: int = Field(default=0)
    strokeLineJoin: str = Field(default="miter")
    strokeUniform: bool = Field(default=False)
    strokeMiterLimit: int = Field(default=4)
    scaleX: float = Field(default=1.0)
    scaleY: float = Field(default=1.0)
    angle: float = Field(default=0.0)
    flipX: bool = Field(default=False)
    flipY: bool = Field(default=False)
    opacity: float = Field(default=1.0)
    shadow: Optional[str] = Field(default=None)
    visible: bool = Field(default=True)
    backgroundColor: str = Field(default="")
    fillRule: str = Field(default="nonzero")
    paintFirst: str = Field(default="fill")
    globalCompositeOperation: str = Field(default="source-over")
    skewX: int = Field(default=0)
    skewY: int = Field(default=0)

    def get_box(self) -> Tuple[int, int, int, int]:
        return (
            round(self.left),
            round(self.top),
            round(self.left + self.width),
            round(self.top + self.height),
        )

    def move(self, destination: Tuple[int, int]) -> None:
        self.left = destination[0]
        self.top = destination[1]

    def shift(self, offset: Tuple[int, int]) -> None:
        self.left += offset[0]
        self.top += offset[1]

    def rotate(self, angle: int) -> None:
        self.angle += angle

    def flip(self, axis: Literal["x", "y"]) -> None:
        if axis == "x":
            self.flipX = not self.flipX
        elif axis == "y":
            self.flipY = not self.flipY
        else:
            raise ValueError(f"Invalid argument for axis: {axis}")

    def scale(self, factor: float, axis: Optional[Literal["x", "y"]] = None) -> None:
        if axis == "x":
            self.scaleX *= factor
        elif axis == "y":
            self.scaleY *= factor
        elif axis is None:
            self.scaleX *= factor
            self.scaleY *= factor
        else:
            raise ValueError(f"Invalid argument for axis: {axis}")

    def __hash__(self) -> int:
        return hash(self.id)

    def __eq__(self, value: object) -> bool:
        return isinstance(value, FabricObject) and value.id == self.id
