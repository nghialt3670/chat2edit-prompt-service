from typing import List, Literal, Union

from pydantic import BaseModel, Field

from core.providers.fabric.models.fabric_image import FabricImage
from core.providers.fabric.models.fabric_object import FabricObject
from core.providers.fabric.models.fabric_textbox import FabricTextbox


class FabricGroup(FabricObject):
    type: Literal["Group"] = Field(default="Group")
    objects: List[Union[FabricImage, FabricTextbox, "FabricGroup"]] = Field(
        default_factory=list
    )
