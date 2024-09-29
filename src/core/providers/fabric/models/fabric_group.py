from typing import List, Literal, Union

from pydantic import BaseModel

from core.providers.fabric.models.fabric_image import FabricImage
from core.providers.fabric.models.fabric_object import FabricObject
from core.providers.fabric.models.fabric_textbox import FabricTextbox


class LayoutManagerModel(BaseModel):
    type: Literal["layoutManager"] = "layoutManager"
    strategy: str = "fit-content"


class FabricGroup(FabricObject):
    type: Literal["Group"] = "Group"
    subTargetCheck: bool = False
    interactive: bool = False
    layoutManager: LayoutManagerModel = LayoutManagerModel()
    objects: List[Union[FabricImage, FabricTextbox, "FabricGroup"]] = []
