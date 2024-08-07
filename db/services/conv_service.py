from typing import List, Optional

from bson import ObjectId
from db.models import Conversation
from pymongo.collection import Collection
from redis import Redis


class ConvService:
    def __init__(self, collection: Collection, redis: Optional[Redis] = None) -> None:
        self._collection = collection
        self._redis = redis

    def find_by_id(self, id: ObjectId) -> Optional[Conversation]:
        # if self._redis and self._redis.exists(str(id)):
        #     return Conversation.parse_raw(self._redis.get(str(id)))

        doc = self._collection.find_one({"_id": ObjectId(id)})
        if doc:
            return Conversation(**doc)

        return None

    def cache(self, conv: Conversation) -> None:
        if self._redis is None:
            raise RuntimeError("No Redis provided")

        self._redis.set(str(conv.id), conv.json())

    def save(self, conv: Conversation, cache: bool = True) -> None:
        self._collection.update_one(
            {"_id": conv.id},
            {"$set": conv.dict(by_alias=True)},
            upsert=True,
        )
        if cache:
            self.cache(conv)
