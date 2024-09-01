import json
from typing import Any, Dict, Optional

from bson import ObjectId
from gridfs import GridFS
from pydantic import BaseModel
from redis import Redis

from core.schemas.fabric import (
    FabricCanvas,
    FabricGroup,
    FabricImage,
    FabricObject,
    FabricRect,
    FabricTextbox,
    LayoutManagerModel,
)


class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, BaseModel):
            obj_dict = obj.dict()
            obj_dict["_type"] = obj.__class__.__name__
            return obj_dict
        return super().default(obj)


class CustomDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        super().__init__(object_hook=self.object_hook, *args, **kwargs)

    def object_hook(self, obj):
        if "_type" in obj:
            obj_type = obj.pop("_type")
            if obj_type == "FabricCanvas":
                return FabricCanvas(**obj)
            if obj_type == "FabricImage":
                return FabricImage(**obj)
            if obj_type == "FabricTextbox":
                return FabricTextbox(**obj)
            if obj_type == "FabricGroup":
                return FabricGroup(**obj)
            if obj_type == "FabricRect":
                return FabricRect(**obj)
            if obj_type == "LayoutManagerModel":
                return LayoutManagerModel(**obj)
            if obj_type == "FabricObject":
                return FabricObject(**obj)
            raise RuntimeError(f"Unsupport obj type: {obj_type}")
        return obj


class ContextService:
    def __init__(
        self, gridfs: GridFS, redis: Optional[Redis], cache_exp_secs: int = 3600
    ) -> None:
        self._gridfs = gridfs
        self._redis = redis
        self._cache_exp_secs = cache_exp_secs

    def update(self, id: ObjectId, context: Dict[str, Any]) -> None:
        if self._gridfs.exists(ObjectId(id)):
            self._gridfs.delete(ObjectId(id))

        json_str = json.dumps(context, cls=CustomEncoder)
        json_bytes = json_str.encode()
        self._gridfs.put(json_bytes, _id=ObjectId(id))
        if self._redis:
            self._redis.set(str(id), json_bytes, self._cache_exp_secs)

    def save(self, context: Dict[str, Any]) -> ObjectId:
        json_str = json.dumps(context, cls=CustomEncoder)
        json_bytes = json_str.encode()
        context_id = self._gridfs.put(json_bytes)
        if self._redis:
            self._redis.set(str(context_id), json_bytes, self._cache_exp_secs)
        return ObjectId(context_id)

    def load(self, id: ObjectId) -> Optional[Dict[str, Any]]:
        if json_bytes := self._redis.get(str(id)):
            return json.loads(json_bytes, cls=CustomDecoder)

        if file_obj := self._gridfs.get(ObjectId(id)):
            return json.loads(file_obj.read(), cls=CustomDecoder)

        return None
