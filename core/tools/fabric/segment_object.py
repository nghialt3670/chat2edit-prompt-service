import os
from typing import Tuple

import aiohttp
import PIL.Image

from core.schemas.fabric import FabricImage
from core.schemas.fabric.fabric_canvas import FabricCanvas
from core.utils.convert import base64_to_image, image_to_base64, src_to_image

ML_SERVICE_BASE_URL = os.getenv("ML_SERVICE_BASE_URL")
ML_SERVICE_API_VERSION = os.getenv("ML_SERVICE_API_VERSION")
SAM_ENDPOINT = f"{ML_SERVICE_BASE_URL}/api/v{ML_SERVICE_API_VERSION}/predict/sam"


async def segment_object(
    canvas: FabricCanvas, box: Tuple[int, int, int, int]
) -> FabricImage:
    src = canvas.backgroundImage.src

    request_data = {"image": {"src": src, "src_type": "data_url"}, "box": box}

    async with aiohttp.ClientSession() as session:
        async with session.post(SAM_ENDPOINT, json=request_data) as response:
            if response.status != 200:
                raise Exception(f"Failed to request object-segmentation model")
            response_dict = await response.json()
            mask = response_dict["mask"]

    base_image = await src_to_image(src)
    mask_base64 = mask["base64"]
    xmin, ymin = mask["offset"]
    mask_image = base64_to_image(mask_base64)
    mask_size = mask_image.size
    mask_box = xmin, ymin, xmin + mask_size[0], ymin + mask_size[1]
    obj_image = PIL.Image.new("RGBA", mask_size)
    obj_image.paste(base_image.crop(mask_box), mask=mask_image)
    obj_base64 = image_to_base64(obj_image)
    data_url = f"data:image/png;base64,{obj_base64}"
    obj = FabricImage(src=data_url, left=xmin, top=ymin, label_to_score={"box": 1.0})
    canvas.objects.append(obj)
    return obj
