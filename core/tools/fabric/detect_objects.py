import os
from typing import List

import aiohttp
import PIL.Image
from core.schemas.fabric import FabricImage
from core.schemas.fabric.fabric_canvas import FabricCanvas
from core.utils.convert import base64_to_image, image_to_base64, src_to_image

ML_SERVICE_BASE_URL = os.getenv("ML_SERVICE_BASE_URL")
ML_SERVICE_API_VERSION = os.getenv("ML_SERVICE_API_VERSION")
GROUNDED_SAM_ENDPOINT = (
    f"{ML_SERVICE_BASE_URL}/api/v{ML_SERVICE_API_VERSION}/predict/grounded-sam"
)


async def detect_objects(canvas: FabricCanvas, prompt: str) -> List[FabricImage]:
    src = canvas.backgroundImage.src

    request_data = {"image": {"src": src, "src_type": "data_url"}, "prompt": prompt}

    async with aiohttp.ClientSession() as session:
        async with session.post(GROUNDED_SAM_ENDPOINT, json=request_data) as response:
            if response.status != 200:
                raise Exception(f"Failed to request object-detection model")
            response_dict = await response.json()
            masks, scores = response_dict["masks"], response_dict["scores"]

    base_image = await src_to_image(src)
    objects = []
    for i in range(len(masks)):
        mask_base64 = masks[i]["base64"]
        xmin, ymin = masks[i]["offset"]
        score = scores[i]
        mask_image = base64_to_image(mask_base64)
        mask_size = mask_image.size
        mask_box = xmin, ymin, xmin + mask_size[0], ymin + mask_size[1]
        obj_image = PIL.Image.new("RGBA", mask_size)
        obj_image.paste(base_image.crop(mask_box), mask=mask_image)
        obj_base64 = image_to_base64(obj_image)
        data_url = f"data:image/png;base64,{obj_base64}"
        obj = FabricImage(
            src=data_url, label_to_score={prompt: score}, left=xmin, top=ymin
        )
        objects.append(obj)

    canvas.objects.extend(objects)
    return objects
