import json
from typing import Any, Dict, Union
from uuid import uuid4

from bson import ObjectId
from gridfs import GridFSBucket
from pymongo.collection import Collection

from models.db.context import Context
from models.db.document import Document
from services.document_service import DocumentService


class ContextService(DocumentService):
    def __init__(self, collection: Collection, bucket: GridFSBucket) -> None:
        super().__init__(collection, Context)
        self._bucket = bucket

    def load(self, id: Union[str, ObjectId]) -> Context:
        context = self.find_by_id(id)
        grid_out = self._bucket.open_download_stream(context.file_id)
        context.data = grid_out.read()
        return context

    def save(self, context: Context) -> None:
        self.update(context)
        self._bucket.delete(context.file_id)
        self._bucket.upload_from_stream_with_id(
            file_id=context.file_id,
            filename=f"{uuid4()}.json",
            source=context.data,
            metadata={"contentType": "application/json"},
        )

    def create(self) -> Context:
        file_id = self._bucket.upload_from_stream(
            filename=f"{uuid4()}.json",
            source=json.dumps({}).encode(),
            metadata={"contentType": "application/json"},
        )
        context = Context(file_id=file_id)
        self.insert_with_id(context)
        return context

    def update(self, document: Document) -> None:
        document_dict = document.model_dump(by_alias=True, exclude={"id", "data"})
        self._collection.update_one(
            {"_id": document.id},
            {"$set": document_dict},
        )
