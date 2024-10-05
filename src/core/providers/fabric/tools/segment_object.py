import io
import json
from typing import Tuple

import aiohttp
import PIL.Image

from core.providers.fabric.models import FabricImage
from core.providers.fabric.models.fabric_canvas import FabricCanvas
from utils.convert import image_to_buffer, image_to_data_url
from utils.env import ENV

API_BASE_URL = ENV.ML_SERVICE_API_BASE_URL
API_VERSION = ENV.ML_SERVICE_API_VERSION
SAM_ENDPOINT = f"{API_BASE_URL}/api/v{API_VERSION}/sam2"


async def segment_object(
    canvas: FabricCanvas, box: Tuple[int, int, int, int]
) -> FabricImage:
    image = canvas.backgroundImage.to_image()
    buffer = image_to_buffer(image)

    form_data = aiohttp.FormData()
    form_data.add_field("image", buffer)
    form_data.add_field("box", json.dumps(box))

    async with aiohttp.ClientSession() as session:
        async with session.post(SAM_ENDPOINT, json=form_data) as response:
            if response.status != 200:
                raise Exception(f"Failed to request segment-anything model")

            response_buffer = await response.read()
            mask = PIL.Image.open(io.BytesIO(response_buffer))

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
        label_to_score={"box": 1.0},
    )
    canvas.objects.append(obj)

    return obj
