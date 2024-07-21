from typing import Dict, List, Optional
from uuid import uuid4

import PIL
import PIL.Image
from core.schemas.fabric.fabric_object import FabricObject
from core.utils.convert import image_to_base64, src_to_image
from pydantic import Field


class FabricImage(FabricObject):
    type: str = "Image"
    cropX: int = 0
    cropY: int = 0
    src: str
    crossOrigin: Optional[str] = None
    filters: List = []

    # Additional attributes
    filename: str = Field(default_factory=lambda: f"{uuid4()}.png")
    label_to_score: Dict[str, float] = {}
    inpainted: bool = False

    async def init_size(self) -> None:
        image = await src_to_image(self.src)
        self.width = image.size[0]
        self.height = image.size[1]

    def set_image(self, image: PIL.Image.Image) -> None:
        image_format = image.format.lower() or "png"
        base64 = image_to_base64(image)
        mime_type = f"image/{image_format}"
        self.src = f"data:{mime_type};base64,{base64}"

    async def to_image(self) -> PIL.Image.Image:
        return await src_to_image(self.src)
