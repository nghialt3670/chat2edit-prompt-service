from base64 import b64decode, b64encode
from io import BytesIO

from PIL import Image


def image_to_base64(image: Image.Image) -> str:
    image_bytes = BytesIO()
    image.format = image.format or "PNG"
    image.save(image_bytes, image.format)
    return b64encode(image_bytes.getvalue()).decode()


def base64_to_image(base64: str) -> Image.Image:
    image_bytes = BytesIO(b64decode(base64))
    return Image.open(image_bytes)


def data_url_to_image(data_url: str) -> Image.Image:
    base64 = data_url.split(",")[1]
    return base64_to_image(base64)


def image_to_mask(image: Image.Image, threshold: int = 0) -> Image.Image:
    grayscale_image = image.convert("L")
    return grayscale_image.point(lambda p: 255 if p > threshold else 0)
