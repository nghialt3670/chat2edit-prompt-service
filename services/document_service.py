from typing import List, Optional, Type, TypeVar, Union

from bson import ObjectId
from pydantic import BaseModel
from pymongo.collection import Collection

from models.db.document import Document

T = TypeVar("T", bound=BaseModel)


class DocumentService:
    def __init__(self, collection: Collection, document_type: Type[T]) -> None:
        self._collection = collection
        self._document_type = document_type

    def find_by_id(self, id: Union[str, ObjectId]) -> Optional[T]:
        id = self._to_object_id(id)
        raw_document = self._collection.find_one({"_id": id})
        if not raw_document:
            return None
        return self._document_type.model_validate(raw_document)

    def insert(self, document: Document) -> Document:
        document_dict = document.model_dump(by_alias=True, exclude={"id"})
        insert_result = self._collection.insert_one(document_dict)
        document.id = insert_result.inserted_id
        return document

    def insert_with_id(self, document: Document) -> None:
        document_dict = document.model_dump(by_alias=True)
        self._collection.insert_one(document_dict)

    def update(self, document: Document) -> None:
        document_dict = document.model_dump(by_alias=True, exclude={"id"})
        self._collection.update_one(
            {"_id": document.id},
            {"$set": document_dict},
        )

    def delete_by_id(self, id: Union[str, ObjectId]) -> None:
        id = self._to_object_id(id)
        self._collection.delete_one({"_id": id})

    def delete_by_ids(self, ids: List[Union[str, ObjectId]]) -> None:
        ids = [self._to_object_id(id) for id in ids]
        self._collection.delete_many({"_id": {"$in": ids}})

    def _to_object_id(self, id: Union[str, ObjectId]) -> ObjectId:
        return ObjectId(id) if not isinstance(id, ObjectId) else id
