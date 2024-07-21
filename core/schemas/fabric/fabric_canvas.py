import json
from io import BytesIO
from typing import Any, List, Optional, Union

from bson import ObjectId
from fastapi import UploadFile
from pydantic import BaseModel, Field

from core.schemas.fabric.fabric_group import FabricGroup
from core.schemas.fabric.fabric_image import FabricImage
from core.schemas.fabric.fabric_textbox import FabricTextbox


class FabricCanvas(BaseModel):
    version: str = "6.0.1"
    backgroundImage: Optional[FabricImage] = None
    objects: List[Union[FabricImage, FabricTextbox, FabricGroup]] = []

    def __deepcopy__(self, memo: dict[int, Any] | None = None) -> "FabricCanvas":
        return super().__deepcopy__(memo)
