from typing import Optional

from pymongo.collection import Collection

from database.models import User
from database.models.user.settings import Settings


class UserService:
    def __init__(self, collection: Collection) -> None:
        self._collection = collection

    def find_by_clerk_user_id(self, id: str) -> Optional[User]:
        doc = self._collection.find_one({"clerk_user_id": id})
        if doc:
            return User(**doc)

        return None

    def save(self, user: User) -> None:
        self._collection.update_one(
            {"_id": user.id}, {"$set": user.dict(by_alias=True)}, upsert=True
        )

    def create_with_clerk_user_id(self, id: str) -> User:
        user = User(clerk_user_id=id)
        self.save(user)
        return user
