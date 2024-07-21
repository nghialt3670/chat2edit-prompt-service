import os
from typing import List

import aiohttp
from core.schemas.fabric.fabric_canvas import FabricCanvas
from core.schemas.fabric.fabric_image import FabricImage
from core.utils.convert import image_to_base64, image_to_mask

ML_SERVICE_BASE_URL = os.getenv("ML_SERVICE_BASE_URL")
ML_SERVICE_API_VERSION = os.getenv("ML_SERVICE_API_VERSION")
LAMA_ENDPOINT = f"{ML_SERVICE_BASE_URL}/api/v{ML_SERVICE_API_VERSION}/predict/lama"


async def inpaint_objects(canvas: FabricCanvas, objects: List[FabricImage]) -> None:
    base_image = canvas.backgroundImage

    if not base_image.is_size_initialized():
        await base_image.init_size()

    request_masks = []
    for obj in objects:
        if obj not in canvas.objects:
            raise RuntimeError("Object not within image")
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
        "expand": True,
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(LAMA_ENDPOINT, json=request_data) as response:
            if response.status != 200:
                raise Exception(f"Failed to request image-inpainting model")
            response_dict = await response.json()

    for obj in objects:
        obj.inpainted = True

    base64 = response_dict["image"]["src"]
    data_url = f"data:image/png;base64,{base64}"
    base_image.src = data_url
