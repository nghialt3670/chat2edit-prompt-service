from typing import Dict, List, Literal, Optional

import PIL.Image
from PIL.Image import Image
from pydantic import Field

from core.providers.fabric.models.fabric_filter import (AdjustableFilter,
                                                        FabricFilter)
from core.providers.fabric.models.fabric_object import FabricObject
from utils.convert import data_url_to_image, image_to_base64


class FabricImage(FabricObject):
    type: Literal["Image"] = Field(default="Image")
    cropX: int = Field(default=0)
    cropY: int = Field(default=0)
    src: str = Field(repr=False)
    filters: List[FabricFilter] = Field(default_factory=list)
    filename: Optional[str] = Field(default=None)
    label_to_score: Optional[Dict[str, float]] = Field(default=None)
    inpainted: Optional[bool] = Field(default=None)

    def apply_filter(self, filt: FabricFilter) -> None:
        if isinstance(filt, AdjustableFilter):
            for curr_filt in self.filters:
                if curr_filt.type == filt.type:
                    curr_filt.merge(filt)
                    return

            self.filters.append(filt)
        else:
            self.filters.append(filt)

    def set_image(self, image: Image) -> None:
        image_format = image.format.lower() or "png"
        base64 = image_to_base64(image)
        mime_type = f"image/{image_format}"
        self.src = f"data:{mime_type};base64,{base64}"
        self.width = image.width
        self.height = image.height

    def to_image(self) -> PIL.Image.Image:
        return data_url_to_image(self.src)
