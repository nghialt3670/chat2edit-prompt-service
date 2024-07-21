from base64 import b64encode

from core.schemas.fabric import FabricCanvas, FabricImage
from fastapi import UploadFile


async def init_canvas_from_file(file: UploadFile) -> FabricCanvas:
    file_bytes = await file.read()
    base64 = b64encode(file_bytes).decode()
    mime_type = file.content_type
    data_url = f"data:{mime_type};base64,{base64}"
    background_image = FabricImage(src=data_url, filename=file.filename)
    return FabricCanvas(backgroundImage=background_image)
