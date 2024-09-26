import aiohttp
from fastapi import FastAPI
from pydantic import BaseModel

from schemas.attachment_schema import AttachmentSchema
from utils.env import ENV
from utils.fetch import fetch_file_as_bytes

app = FastAPI()


class File(BaseModel):
    data: bytes
    name: str
    content_type: str

    @classmethod
    async def from_attachment(cls, attachment: AttachmentSchema) -> "File":
        api_base_url = ENV.ATTACHMENT_SERVICE_API_BASE_URL
        endpoint = f"{api_base_url}/file?attachmentId={attachment.id}"
        data = await fetch_file_as_bytes(endpoint)
        return cls(
            data=data,
            name=attachment.file.name,
            content_type=attachment.file.contentType,
        )
