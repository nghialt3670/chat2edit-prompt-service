from typing import List, Union

from core.schemas.fabric.fabric_image import FabricImage
from core.schemas.fabric.fabric_object import FabricObject
from core.schemas.fabric.fabric_textbox import FabricTextbox
from pydantic import BaseModel


class LayoutManagerModel(BaseModel):
    type: str = "layoutManager"
    strategy: str = "fit-content"


class FabricGroup(FabricObject):
    type: str = "Group"
    subTargetCheck: bool = False
    interactive: bool = False
    layoutManager: LayoutManagerModel = LayoutManagerModel()
    objects: List[Union[FabricImage, FabricTextbox, "FabricGroup"]] = []
