from typing import List, Optional

from bson import ObjectId
from pymongo.collection import Collection
from redis import Redis

from database.models import Conv


class ConvService:
    def __init__(self, collection: Collection, redis: Optional[Redis] = None) -> None:
        self._collection = collection
        self._redis = redis

    def find_by_id(self, id: ObjectId) -> Optional[Conv]:
        if self._redis and self._redis.exists(str(id)):
            return self._redis.get(str(id))

        doc = self._collection.find_one({"_id": ObjectId(id)})
        if doc:
            return Conv(**doc)

        return None

    def find_by_id_and_user_id(self, id: ObjectId, user_id: ObjectId) -> Optional[Conv]:
        query = {"_id": ObjectId(id), "user_id": ObjectId(user_id)}
        doc = self._collection.find_one(query)
        if doc:
            return Conv(**doc)
        return None

    def find_one_by_user_id(self, user_id: ObjectId) -> Optional[Conv]:
        return self._collection.find_one({"user_id": ObjectId(user_id)})

    def find_by_user_id(
        self, user_id: ObjectId, limit: int = -1, offset: int = 0
    ) -> List[Conv]:
        cursor = self._collection.find({"user_id": ObjectId(user_id)}).skip(offset)

        if limit > 0:
            cursor = cursor.limit(limit)

        convs = [Conv(**doc) for doc in cursor]
        return convs

    def cache(self, conv: Conv) -> None:
        if self._redis is None:
            raise RuntimeError("No Redis provided")

        self._redis.set(str(conv.id), conv.json())

    def save(self, conv: Conv, cache: bool = True) -> None:
        self._collection.update_one(
            {"_id": conv.id},
            {"$set": conv.dict(by_alias=True)},
            upsert=True,
        )
        if cache:
            self.cache(conv)
