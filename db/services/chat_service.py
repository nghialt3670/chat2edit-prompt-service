from typing import Optional, Union

from bson import ObjectId
from pymongo.collection import Collection
from redis import Redis

from db.models import Chat


class ChatService:
    def __init__(
        self,
        collection: Collection,
        redis: Optional[Redis] = None,
        cache_exp_secs: int = 3600,
    ) -> None:
        self._collection = collection
        self._redis = redis
        self._cache_exp_secs = cache_exp_secs

    def load(self, id: Union[ObjectId, str]) -> Optional[Chat]:
        if self._redis:
            data = self._redis.get(str(id))
            if data:
                return Chat.parse_raw(data)

        doc = self._collection.find_one({"_id": ObjectId(id)})
        return Chat(**doc) if doc else None

    def save(self, chat: Chat) -> None:
        self._collection.update_one(
            {"_id": chat.id},
            {"$set": chat.dict(by_alias=True)},
            upsert=True,
        )
        if self._redis:
            self._redis.set(str(chat.id), chat.json(), self._cache_exp_secs)
