from typing import Any, List, Optional, Union

from pydantic import BaseModel

from core.providers.fabric.models.fabric_group import FabricGroup
from core.providers.fabric.models.fabric_image import FabricImage
from core.providers.fabric.models.fabric_rect import FabricRect
from core.providers.fabric.models.fabric_textbox import FabricTextbox


class FabricCanvas(BaseModel):
    version: str = "6.0.1"
    backgroundImage: Optional[FabricImage] = None
    objects: List[Union[FabricImage, FabricTextbox, FabricRect, FabricGroup]] = []
