from typing import Any, List, Optional, Union

from pydantic import BaseModel

from core.schemas.fabric.fabric_group import FabricGroup
from core.schemas.fabric.fabric_image import FabricImage
from core.schemas.fabric.fabric_rect import FabricRect
from core.schemas.fabric.fabric_textbox import FabricTextbox


class FabricCanvas(BaseModel):
    version: str = "6.0.1"
    backgroundImage: Optional[FabricImage] = None
    objects: List[Union[FabricImage, FabricTextbox, FabricRect, FabricGroup]] = []

    def __deepcopy__(self, memo: dict[int, Any] | None = None) -> "FabricCanvas":
        return super().__deepcopy__(memo)
