from xmlrpc.client import boolean
from bson import ObjectId
from fastapi import UploadFile
from gridfs import GridFS


class FileService:
    def __init__(self, gridfs: GridFS) -> None:
        self._gridfs = gridfs

    def exist(self, id: str) -> bool:
        return self._gridfs.exists(ObjectId(id))

    async def save_upload_file(self, file: UploadFile, id: str, user_id: str) -> str:
        content = await file.read()
        return self._gridfs.put(
            content, _id=ObjectId(id), filename=file.filename, user_id=user_id
        )

    def get(self, id: str):
        return self._gridfs.get(ObjectId(id))
