import os
from copy import deepcopy
from typing import List

import aiohttp

from core.schemas.fabric.fabric_canvas import FabricCanvas
from core.schemas.fabric.fabric_object import FabricObject
from core.utils.convert import image_to_base64, image_to_mask

ML_SERVICE_BASE_URL = os.getenv("ML_SERVICE_BASE_URL")
ML_SERVICE_API_VERSION = os.getenv("ML_SERVICE_API_VERSION")
STABLE_DIFFUSION_INPAINT_ENDPOINT = f"{ML_SERVICE_BASE_URL}/api/v{ML_SERVICE_API_VERSION}/predict/stable-diffusion-inpaint"


async def replace_objects_with_prompt(
    canvas: FabricCanvas, objects: List[FabricObject], prompt: str
) -> FabricCanvas:
    base_image = canvas.backgroundImage

    if not base_image.is_size_initialized():
        await base_image.init_size()

    request_masks = []
    for obj in objects:
        obj_image = await obj.to_image()
        obj_mask = image_to_mask(obj_image)
        request_mask = {
            "base64": image_to_base64(obj_mask),
            "original_size": (base_image.width, base_image.height),
            "offset": (obj.left, obj.top),
        }
        request_masks.append(request_mask)

    request_data = {
        "image": {
            "src": base_image.src,
        },
        "masks": request_masks,
        "prompt": prompt,
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(
            STABLE_DIFFUSION_INPAINT_ENDPOINT, json=request_data
        ) as response:
            if response.status != 200:
                raise Exception(f"Failed to request stable-diffusion model")
            response_dict = await response.json()

    for obj in objects:
        obj.inpainted = True

    base64 = response_dict["image"]["src"]
    data_url = f"data:image/png;base64,{base64}"
    base_image.src = data_url
