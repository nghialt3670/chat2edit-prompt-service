import copy
from typing import Dict, List, Optional, Tuple, Union

from chat2edit.providers.fabric.models.fabric_object import FabricObject
from chat2edit.utils.image import data_url_to_pil_image, pil_image_to_data_url
from PIL import Image
from pydantic import Field


class FabricImage(FabricObject):
    cropX: Optional[int] = Field(default=None, repr=False)
    cropY: Optional[int] = Field(default=None, repr=False)
    filters: List[Dict[str, Union[str, float]]] = Field(
        default_factory=list, repr=False
    )
    src: str = Field(repr=False)

    def get_box(self) -> Tuple[int, int, int, int]:
        return tuple(int(x) for x in super().get_box())

    def to_image(self) -> Image.Image:
        return data_url_to_pil_image(self.src)

    def get_copy(self) -> "FabricImage":
        return FabricImage(
            **FabricObject.get_copy(self).__dict__,
            cropX=self.cropX,
            cropY=self.cropY,
            filters=[copy.deepcopy(f) for f in self.filters],
            src=self.src,
        )
