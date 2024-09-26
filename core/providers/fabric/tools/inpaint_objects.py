import os
from typing import List

import aiohttp

from core.providers.fabric.models.fabric_canvas import FabricCanvas
from core.providers.fabric.models.fabric_image import FabricImage
from utils.convert import image_to_base64, image_to_mask
from utils.env import ENV

API_BASE_URL = ENV.ML_SERVICE_API_BASE_URL
API_VERSION = ENV.ML_SERVICE_API_VERSION
LAMA_ENDPOINT = f"{API_BASE_URL}/api/v{API_VERSION}/predict/lama"


async def inpaint_objects(canvas: FabricCanvas, object_idxs: List[int]) -> None:
    base_image = canvas.backgroundImage

    if not base_image.is_size_initialized():
        await base_image.init_size()

    request_masks = []
    for i in object_idxs:
        obj = canvas.objects[i]
        if not isinstance(obj, FabricImage) or not obj.label_to_score or obj.inpainted:
            continue
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

    for i in object_idxs:
        canvas.objects[i].inpainted = True

    base64 = response_dict["image"]["src"]
    data_url = f"data:image/png;base64,{base64}"
    base_image.src = data_url
