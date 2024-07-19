import os

from chat2edit.providers.fabric.models.fabric_image import FabricImage
from chat2edit.utils.image import pil_image_to_data_url
from PIL import Image


class FabricUploadedImage(FabricImage):
    filename: str

    @classmethod
    def from_file(cls, path: str) -> "FabricUploadedImage":
        pil_image = Image.open(path)
        return cls(
            type="image",
            src=pil_image_to_data_url(pil_image),
            width=pil_image.width,
            height=pil_image.height,
            filename=os.path.basename(path),
        )

    def get_copy(self) -> "FabricUploadedImage":
        return FabricUploadedImage(
            **FabricImage.get_copy(self).__dict__,
            filename=self.filename,
        )
