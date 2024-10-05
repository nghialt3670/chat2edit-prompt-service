from typing import Literal, Optional, Tuple
from uuid import uuid4

from pydantic import BaseModel, Field


class FabricObject(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    angle: float = Field(default=0.0)
    left: float = Field(default=0.0)
    top: float = Field(default=0.0)
    width: float = Field(default=0.0)
    height: float = Field(default=0.0)
    scaleX: float = Field(default=1.0)
    scaleY: float = Field(default=1.0)
    flipX: bool = Field(default=False)
    flipY: bool = Field(default=False)
    opacity: float = Field(default=1.0)
    fill: str = Field(default="rgb(0,0,0)")

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

    def __hash__(self) -> int:
        return hash(self.id)

    def __eq__(self, value: object) -> bool:
        return isinstance(value, FabricObject) and value.id == self.id
