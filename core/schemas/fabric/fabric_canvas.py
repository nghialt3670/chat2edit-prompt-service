import json
from io import BytesIO
from typing import Any, List, Optional, Union

from fastapi import UploadFile
from pydantic import BaseModel

from core.schemas.fabric.fabric_group import FabricGroup
from core.schemas.fabric.fabric_image import FabricImage
from core.schemas.fabric.fabric_textbox import FabricTextbox


class FabricCanvas(BaseModel):
    version: str = "6.0.1"
    backgroundImage: Optional[FabricImage] = None
    objects: List[Union[FabricImage, FabricTextbox, FabricGroup]] = []

    def __deepcopy__(self, memo: dict[int, Any] | None = None) -> "FabricCanvas":
        return super().__deepcopy__(memo)

    @classmethod
    async def from_file(cls, file: UploadFile) -> "FabricCanvas":
        return cls(**json.loads(await file.read()))

    def to_file(self) -> UploadFile:
        json_str = self.model_dump_json()
        file_bytes = json_str.encode()
        file_buffer = BytesIO(file_bytes)
        filename = self.backgroundImage.filename.split(".").pop().join(".") + ".canvas"
        file = UploadFile(file_buffer, filename=filename)
        return file
