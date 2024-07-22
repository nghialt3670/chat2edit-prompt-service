from typing import Any

from bson import ObjectId
from core.schemas.fabric.fabric_canvas import FabricCanvas
from fastapi import UploadFile
from gridfs import GridFS


class CanvasService:
    def __init__(self, gridfs: GridFS) -> None:
        self._gridfs = gridfs

    async def save_from_upload_file(
        self, file: UploadFile, user_id: ObjectId
    ) -> ObjectId:
        return self._gridfs.put(
            await file.read(), filename=file.filename, user_id=ObjectId(user_id)
        )

    def save(self, canvas: FabricCanvas, user_id: ObjectId) -> ObjectId:
        return self._gridfs.put(
            canvas.model_dump_json().encode(),
            filename=".".join(canvas.backgroundImage.filename.split(".")[:-1])
            + ".canvas",
            user_id=ObjectId(user_id),
        )

    def get(self, id: ObjectId) -> Any:
        return self._gridfs.get(ObjectId(id))

    def load(self, id: ObjectId) -> FabricCanvas:
        return FabricCanvas.model_validate_json(self._gridfs.get(ObjectId(id)).read())
