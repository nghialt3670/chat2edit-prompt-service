from typing import Iterable, Optional

from pydantic import Field

from core.providers.fabric.models.fabric_collection import FabricCollection

FONT_PATH = "chat2edit/resources/fonts/Arial.ttf"


class FabricCanvas(FabricCollection):
    backgroundImage: FabricUploadedImage

    def annotate(self, objects: Iterable[FabricObject]) -> None:
        self.annotated = True
        for i, obj in enumerate(objects):
            if obj not in self.objects:
                CONSOLE_LOGGER.warning(
                    "Atempt to annotate object that not belong to canvas"
                )
            obj.annotate(i + 1)

    def unannotate(self, objects: Optional[Iterable[FabricObject]] = None) -> None:
        self.annotated = False
        objects = objects or self.objects
        for obj in objects:
            obj.unannotate()

    def to_image(self) -> Image.Image:
        bg_pil_image = data_url_to_pil_image(self.backgroundImage.src)
        for obj in self.objects:
            if obj.type == "image":
                obj_pil_image = data_url_to_pil_image(obj.src)
                obj_pil_image = obj_pil_image.rotate(obj.angle)
                if obj.flipX:
                    obj_pil_image = obj_pil_image.transpose(Image.FLIP_LEFT_RIGHT)
                if obj.flipY:
                    obj_pil_image = obj_pil_image.transpose(Image.FLIP_TOP_BOTTOM)

                obj_position = (obj.left, obj.top)
                obj_scaled_size = (
                    int(obj.width * obj.scaleX),
                    int(obj.height * obj.scaleY),
                )
                obj_pil_image = obj_pil_image.resize(obj_scaled_size)
                bg_pil_image.paste(obj_pil_image, obj_position, obj_pil_image)

            elif obj.type == "textbox":
                draw = ImageDraw.Draw(bg_pil_image)
                position = (obj.left, obj.top)
                text = obj.text
                font = ImageFont.truetype(FONT_PATH, obj.fontSize)
                draw.text(position, text, font=font)

        return bg_pil_image

    def get_id(self) -> str:
        return self.id

    def get_type(self) -> str:
        if self.annotated:
            return "annotated_image"
        return "image"

    def get_copy(self) -> "FabricCanvas":
        return FabricCanvas(
            annotated=self.annotated,
            backgroundImage=self.backgroundImage.get_copy(),
            objects=[obj.get_copy() for obj in self.objects],
        )
