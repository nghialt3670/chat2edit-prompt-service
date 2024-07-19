from bson import ObjectId
from fastapi import UploadFile
from gridfs import GridFS


class FileService:
    def __init__(self, gridfs: GridFS) -> None:
        self._gridfs = gridfs

    async def save_upload_file(self, file: UploadFile, user_id: str) -> str:
        content = await file.read()
        return self._gridfs.put(content, filename=file.filename, user_id=user_id)

    def get(self, id: str):
        return self._gridfs.get(ObjectId(id))
