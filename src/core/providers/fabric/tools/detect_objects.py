import io
import zipfile
from typing import List

import aiohttp
import PIL.Image
from PIL.Image import Image

from core.providers.fabric.models import FabricImage
from core.providers.fabric.models.fabric_canvas import FabricCanvas
from utils.convert import image_to_buffer, image_to_data_url
from utils.env import ENV

API_URL = ENV.ML_SERVICE_API_BASE_URL
API_VERSION = ENV.ML_SERVICE_API_VERSION
GROUNDED_SAM_ENDPOINT = f"{API_URL}/api/v{API_VERSION}/grounded-sam"


async def detect_objects(canvas: FabricCanvas, prompt: str) -> List[FabricImage]:
    image = canvas.backgroundImage.to_image()
    buffer = image_to_buffer(image)

    form_data = aiohttp.FormData()
    form_data.add_field("image", buffer)
    form_data.add_field("prompt", prompt)

    async with aiohttp.ClientSession() as session:
        async with session.post(GROUNDED_SAM_ENDPOINT, data=form_data) as response:
            if response.status != 200:
                raise Exception(f"Failed to request object-detection model")

            scores: List[float] = []
            masks: List[Image] = []
            zip_bytes = await response.read()

            with zipfile.ZipFile(io.BytesIO(zip_bytes)) as z:
                for file_info in z.infolist():
                    score = float(file_info.filename.split(".")[0])
                    scores.append(score)
                    with z.open(file_info) as file:
                        mask = Image.open(file)
                        masks.append(mask)

    detected_objects = []

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
        )
        canvas.objects.append(obj)
        detected_objects.append(obj)

    return detected_objects
