import io
import json
import zipfile
from typing import Any, List, Literal, Optional, Tuple, Union

import aiohttp
import PIL
import PIL.Image
from PIL.Image import Image
from pydantic import BaseModel, Field

from core.providers.fabric.models.fabric_filter import FabricFilter
from core.providers.fabric.models.fabric_group import FabricGroup
from core.providers.fabric.models.fabric_image import FabricImage
from core.providers.fabric.models.fabric_object import FabricObject
from core.providers.fabric.models.fabric_rect import FabricRect
from core.providers.fabric.models.fabric_textbox import FabricTextbox
from utils.convert import image_to_buffer, image_to_data_url, image_to_mask
from utils.env import ENV

GROUNDED_SAM_ENDPOINT = (
    f"{ENV.ML_SERVICE_API_BASE_URL}/api/v{ENV.ML_SERVICE_API_VERSION}/grounded-sam"
)
SAM2_ENDPOINT = f"{ENV.ML_SERVICE_API_BASE_URL}/api/v{ENV.ML_SERVICE_API_VERSION}/sam2"
LAMA_ENDPOINT = f"{ENV.ML_SERVICE_API_BASE_URL}/api/v{ENV.ML_SERVICE_API_VERSION}/lama"
SD_INPAINT_ENDPOINT = (
    f"{ENV.ML_SERVICE_API_BASE_URL}/api/v{ENV.ML_SERVICE_API_VERSION}/sd-inpaint"
)


class FabricCanvas(BaseModel):
    backgroundImage: Optional[FabricImage] = Field(default=None)
    objects: List[Union[FabricImage, FabricTextbox, FabricRect, FabricGroup]] = Field(
        default_factory=list
    )

    async def segment_image_objects_by_prompt(self, prompt: str) -> List[FabricImage]:
        image = self.backgroundImage.to_image()
        buffer = image_to_buffer(image)

        form_data = aiohttp.FormData()
        form_data.add_field("image", buffer)
        form_data.add_field("prompt", prompt)

        async with aiohttp.ClientSession() as session:
            async with session.post(GROUNDED_SAM_ENDPOINT, data=form_data) as response:
                if response.status != 200:
                    raise Exception(f"Failed to request object-segmentation model")

                scores: List[float] = []
                masks: List[Image] = []
                zip_bytes = await response.read()

                with zipfile.ZipFile(io.BytesIO(zip_bytes)) as z:
                    for file_info in z.infolist():
                        score = float(file_info.filename.split(".")[0])
                        scores.append(score)
                        with z.open(file_info) as file:
                            mask = PIL.Image.open(file)
                            mask.load()
                            masks.append(mask)

        objects = []

        for score, mask in zip(scores, masks):
            obj_box = mask.getbbox()
            obj_mask = mask.crop(obj_box)
            obj_image = PIL.Image.new("RGBA", obj_mask.size)
            obj_image.paste(image.crop(obj_box), mask=obj_mask)
            data_url = image_to_data_url(obj_image)
            obj = FabricImage(
                src=data_url,
                left=obj_box[0],
                top=obj_box[1],
                width=obj_image.width,
                height=obj_image.height,
                label_to_score={prompt: score},
                inpainted=False,
            )
            self.objects.append(obj)
            objects.append(obj)

        return objects

    async def segment_image_objects_by_boxes(
        self, boxes: List[Tuple[int, int, int, int]]
    ) -> List[FabricImage]:
        image = self.backgroundImage.to_image()
        buffer = image_to_buffer(image)

        form_data = aiohttp.FormData()
        form_data.add_field("image", buffer)
        form_data.add_field("boxes", json.dumps(boxes))

        async with aiohttp.ClientSession() as session:
            async with session.post(SAM2_ENDPOINT, data=form_data) as response:
                if response.status != 200:
                    raise Exception(f"Failed to request object-segmentation model")

                masks: List[Image] = []
                zip_bytes = await response.read()

                with zipfile.ZipFile(io.BytesIO(zip_bytes)) as z:
                    for file_info in z.infolist():
                        with z.open(file_info) as file:
                            mask = PIL.Image.open(file)
                            mask.load()
                            masks.append(mask)

        objects = []

        for mask in masks:
            obj_box = mask.getbbox()
            obj_mask = mask.crop(obj_box)
            obj_image = PIL.Image.new("RGBA", obj_mask.size)
            obj_image.paste(image.crop(obj_box), mask=obj_mask)
            data_url = image_to_data_url(obj_image)
            obj = FabricImage(
                src=data_url,
                left=obj_box[0],
                top=obj_box[1],
                width=obj_image.width,
                height=obj_image.height,
                inpainted=False,
            )
            self.objects.append(obj)
            objects.append(obj)

        return objects

    async def inpaint_image_objects(self, objects: List[FabricImage]) -> None:
        if not objects:
            return

        image = self.backgroundImage.to_image()
        mask = PIL.Image.new("L", image.size)

        for obj in objects:
            obj_image = obj.to_image()
            obj_mask = image_to_mask(obj_image)
            mask.paste(obj_mask, obj.get_box(), obj_mask)

        image_buffer = image_to_buffer(image)
        mask_buffer = image_to_buffer(mask)

        form_data = aiohttp.FormData()
        form_data.add_field("image", image_buffer)
        form_data.add_field("mask", mask_buffer)

        async with aiohttp.ClientSession() as session:
            async with session.post(LAMA_ENDPOINT, data=form_data) as response:
                if response.status != 200:
                    raise Exception(f"Failed to request image-inpainting model")

                response_buffer = await response.read()
                inpainted_image = PIL.Image.open(io.BytesIO(response_buffer))
                inpainted_image.load()

        for obj in objects:
            obj.inpainted = True

        self.backgroundImage.set_image(inpainted_image)

    async def inpaint_image_objects_by_prompt(
        self, objects: List[FabricImage], prompt: str
    ) -> None:
        if not objects:
            return

        image = self.backgroundImage.to_image()
        mask = PIL.Image.new("L", image.size)

        for obj in objects:
            obj_image = obj.to_image()
            obj_mask = image_to_mask(obj_image)
            mask.paste(obj_mask, obj.get_box(), obj_mask)

        image_buffer = image_to_buffer(image)
        mask_buffer = image_to_buffer(mask)

        form_data = aiohttp.FormData()
        form_data.add_field("image", image_buffer)
        form_data.add_field("mask", mask_buffer)
        form_data.add_field("prompt", prompt)

        async with aiohttp.ClientSession() as session:
            async with session.post(SD_INPAINT_ENDPOINT, data=form_data) as response:
                if response.status != 200:
                    raise Exception(f"Failed to request image-inpainting model")

                response_buffer = await response.read()
                inpainted_image = PIL.Image.open(io.BytesIO(response_buffer))
                inpainted_image.load()

        for obj in objects:
            obj.inpainted = True

        self.backgroundImage.set_image(inpainted_image)

    async def insert_objects(self, objects: List[FabricObject]) -> None:
        self.objects.extend(objects)
        
    async def replace_objects_by_prompt(self, objects: List[FabricObject], prompt: str) -> None:
        uninpainted_objects = self._get_uninpainted_image_objects(objects)
        await self.inpaint_image_objects_by_prompt(uninpainted_objects, prompt)
        ids_to_remove = set(obj.id for obj in objects)
        self.objects = [obj for obj in self.objects if obj.id not in ids_to_remove]

    async def remove_objects(self, objects: List[FabricObject]) -> None:
        uninpainted_objects = self._get_uninpainted_image_objects(objects)
        await self.inpaint_image_objects(uninpainted_objects)
        ids_to_remove = set(obj.id for obj in objects)
        self.objects = [obj for obj in self.objects if obj.id not in ids_to_remove]

    async def flip_objects(
        self, objects: List[FabricObject], axes: List[Literal["x", "y"]]
    ) -> None:
        uninpainted_objects = self._get_uninpainted_image_objects(objects)
        await self.inpaint_image_objects(uninpainted_objects)
        for i in self._get_object_indexes(objects):
            self.objects[i].flip(axes.pop())

    async def move_objects(
        self, objects: List[FabricObject], destinations: List[Tuple[int, int]]
    ) -> None:
        uninpainted_objects = self._get_uninpainted_image_objects(objects)
        await self.inpaint_image_objects(uninpainted_objects)
        for i in self._get_object_indexes(objects):
            self.objects[i].move(destinations.pop())

    async def shift_objects(
        self, objects: List[FabricObject], offsets: List[Tuple[int, int]]
    ) -> None:
        uninpainted_objects = self._get_uninpainted_image_objects(objects)
        await self.inpaint_image_objects(uninpainted_objects)
        for i in self._get_object_indexes(objects):
            self.objects[i].shift(offsets.pop())

    async def rotate_objects(
        self, objects: List[FabricObject], angles: List[float]
    ) -> None:
        uninpainted_objects = self._get_uninpainted_image_objects(objects)
        await self.inpaint_image_objects(uninpainted_objects)
        for i in self._get_object_indexes(objects):
            self.objects[i].rotate(angles.pop())

    async def scale_objects(
        self, objects: List[FabricObject], factors: List[float]
    ) -> None:
        uninpainted_objects = self._get_uninpainted_image_objects(objects)
        await self.inpaint_image_objects(uninpainted_objects)
        for i in self._get_object_indexes(objects):
            self.objects[i].scale(factors[i])

    def apply_filter(
        self, filt: FabricFilter, objects: Optional[List[FabricImage]] = None
    ) -> None:
        if objects:
            for i in self._get_object_indexes(objects):
                self.objects[i].apply_filter(filt)
        else:
            self.backgroundImage.apply_filter(filt)
            for obj in self.objects:
                if isinstance(obj, FabricImage):
                    obj.apply_filter(filt)

    def _get_uninpainted_image_objects(
        self, objects: List[FabricObject]
    ) -> List[FabricImage]:
        return [
            obj
            for obj in objects
            if isinstance(obj, FabricImage) and obj.inpainted == False
        ]

    def _get_object_indexes(self, objects: List[FabricObject]) -> List[int]:
        return [self.objects.index(obj) for obj in objects]
