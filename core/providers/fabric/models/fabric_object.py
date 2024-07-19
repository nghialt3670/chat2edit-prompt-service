from typing import Optional, Tuple

from chat2edit.utils.models import create_id
from pydantic import BaseModel, Field


class FabricObject(BaseModel):
    id: str = Field(default_factory=create_id, repr=False)
    type: str = Field(repr=False)
    angle: float = Field(default=0.0, repr=False)
    flipX: bool = Field(default=False, repr=False)
    flipY: bool = Field(default=False, repr=False)
    scaleX: float = Field(default=1.0, repr=False)
    scaleY: float = Field(default=1.0, repr=False)
    left: int = Field(default=0, repr=False)
    top: int = Field(default=0, repr=False)
    opacity: float = Field(default=1.0, repr=False)
    fill: Optional[str] = Field(default=None, repr=False)
    shadow: Optional[str] = Field(default=None, repr=False)
    stroke: Optional[str] = Field(default=None, repr=False)
    strokeWidth: int = Field(default=0, repr=False)
    showBox: bool = Field(default=False, repr=False)
    index: Optional[int] = Field(default=None, repr=False)
    width: Optional[float] = Field(default=None, repr=False)
    height: Optional[float] = Field(default=None, repr=False)

    def annotate(self, index: int) -> None:
        self.showBox = True
        self.index = index

    def unannotate(self) -> None:
        self.showBox = False
        self.index = None

    def get_box(self) -> Tuple[int, int, int, int]:
        return self.left, self.top, self.left + self.width, self.top + self.height

    def get_copy(self) -> "FabricObject":
        return FabricObject(
            type=self.type,
            angle=self.angle,
            flipX=self.flipX,
            flipY=self.flipY,
            scaleX=self.scaleX,
            scaleY=self.scaleY,
            left=self.left,
            top=self.top,
            opacity=self.opacity,
            fill=self.fill,
            shadow=self.shadow,
            stroke=self.stroke,
            strokeWidth=self.strokeWidth,
            showBox=self.showBox,
            index=self.index,
            width=self.width,
            height=self.height,
        )

    def __hash__(self) -> int:
        return hash(self.id)
