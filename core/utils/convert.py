from base64 import b64decode, b64encode
from io import BytesIO

import aiohttp
import PIL.Image


def image_to_base64(image: PIL.Image.Image) -> str:
    image_bytes = BytesIO()
    image.format = image.format or "PNG"
    image.save(image_bytes, image.format)
    return b64encode(image_bytes.getvalue()).decode()


def base64_to_image(base64: str) -> PIL.Image.Image:
    image_bytes = BytesIO(b64decode(base64))
    return PIL.Image.open(image_bytes)


async def http_url_to_image(http_url: str) -> PIL.Image.Image:
    async with aiohttp.ClientSession() as session:
        async with session.get(http_url) as response:
            image_bytes = await response.read()
        return PIL.Image.open(BytesIO(image_bytes))


async def src_to_image(src: str) -> PIL.Image.Image:
    if src.startswith("http:") or src.startswith("https:"):
        return await http_url_to_image(src)
    if src.startswith("data:"):
        base64 = src.split(",")[1]
        return base64_to_image(base64)
    return base64_to_image(src)


def image_to_mask(image: PIL.Image.Image, threshold: int = 0) -> PIL.Image.Image:
    grayscale_image = image.convert("L")
    return grayscale_image.point(lambda p: 255 if p > threshold else 0)
