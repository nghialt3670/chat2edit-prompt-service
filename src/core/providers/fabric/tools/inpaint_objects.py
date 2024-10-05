import io
from typing import List

import aiohttp
import PIL
import PIL.Image

from core.providers.fabric.models.fabric_canvas import FabricCanvas
from core.providers.fabric.models.fabric_image import FabricImage
from utils.convert import image_to_buffer, image_to_mask
from utils.env import ENV

API_BASE_URL = ENV.ML_SERVICE_API_BASE_URL
API_VERSION = ENV.ML_SERVICE_API_VERSION
LAMA_ENDPOINT = f"{API_BASE_URL}/api/v{API_VERSION}/lama"


async def inpaint_objects(canvas: FabricCanvas, object_idxs: List[int]) -> None:
    image = canvas.backgroundImage.to_image()
    mask = PIL.Image.new("L", image.size)

    for i in object_idxs:
        obj = canvas.objects[i]

        if not isinstance(obj, FabricImage) or not obj.label_to_score or obj.inpainted:
            continue

        obj_image = await obj.to_image()
        obj_mask = image_to_mask(obj_image)
        mask.paste(obj_mask, mask=obj_mask)

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

    for i in object_idxs:
        canvas.objects[i].inpainted = True

    canvas.backgroundImage.set_image(inpainted_image)
