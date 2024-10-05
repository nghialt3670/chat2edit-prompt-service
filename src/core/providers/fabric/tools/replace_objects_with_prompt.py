import io
import os
from copy import deepcopy
from typing import List

import aiohttp
import PIL
import PIL.Image

from core.providers.fabric.models.fabric_canvas import FabricCanvas
from core.providers.fabric.models.fabric_image import FabricImage
from core.providers.fabric.models.fabric_object import FabricObject
from utils.convert import image_to_base64, image_to_buffer, image_to_mask
from utils.env import ENV

API_BASE_URL = ENV.ML_SERVICE_API_BASE_URL
API_VERSION = ENV.ML_SERVICE_API_VERSION
SD_INPAINT_ENDPOINT = f"{API_BASE_URL}/api/v{API_VERSION}/sd-inpaint"


async def replace_objects_with_prompt(
    canvas: FabricCanvas, objects: List[FabricObject], prompt: str
) -> FabricCanvas:
    canvas = deepcopy(canvas)

    image = canvas.backgroundImage.to_image()
    mask = PIL.Image.new("L", image.size)

    for obj in objects:
        obj_image = await obj.to_image()
        obj_mask = image_to_mask(obj_image)
        mask.paste(obj_mask, mask=obj_mask)

    image_buffer = image_to_buffer(image)
    mask_buffer = image_to_buffer(mask)

    form_data = aiohttp.FormData()
    form_data.add_field("image", image_buffer)
    form_data.add_field("mask", mask_buffer)
    form_data.add_field("prompt", prompt)

    async with aiohttp.ClientSession() as session:
        async with session.post(SD_INPAINT_ENDPOINT, data=form_data) as response:
            if response.status != 200:
                raise Exception(f"Failed to request stable-diffusion-inpaint model")

            response_buffer = await response.read()
            inpainted_image = PIL.Image.open(io.BytesIO(response_buffer))

    for obj in objects:
        canvas.objects.remove(obj)

    canvas.backgroundImage.set_image(inpainted_image)
