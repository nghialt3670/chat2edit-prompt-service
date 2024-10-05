from typing import Any, List, Optional, Union

from pydantic import BaseModel, Field

from core.providers.fabric.models.fabric_group import FabricGroup
from core.providers.fabric.models.fabric_image import FabricImage
from core.providers.fabric.models.fabric_rect import FabricRect
from core.providers.fabric.models.fabric_textbox import FabricTextbox


class FabricCanvas(BaseModel):
    backgroundImage: Optional[FabricImage] = Field(default=None)
    objects: List[Union[FabricImage, FabricTextbox, FabricRect, FabricGroup]] = Field(
        default_factory=list
    )
