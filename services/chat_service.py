from typing import List, Optional, Union

from bson import ObjectId
from pymongo.collection import Collection

from models.db.account import Account
from models.db.chat import Chat
from models.db.context import Context
from services.document_service import DocumentService


class ChatService(DocumentService):
    def __init__(self, collection: Collection) -> None:
        super().__init__(collection, Chat)

    def find_by_id_and_account_id(
        self, id: Union[str, ObjectId], account_id: Union[str, ObjectId]
    ) -> Optional[Chat]:
        chat = self.find_by_id(id)
        if chat and chat.account_id == account_id:
            return chat

        return None

    def find_many_by_account_id(
        self, account_id: Union[str, ObjectId], limit: int = 0
    ) -> List[Chat]:
        account_id = self._to_object_id(account_id)
        raw_chats = (
            self._collection.find({"account_id": account_id})
            .limit(limit)
            .sort("updated_at")
        )
        return [Chat.model_validate(chat) for chat in raw_chats]

    def create(self, account: Account, context: Context) -> Chat:
        chat = Chat(
            account_id=account.id,
            context_id=context.id,
            settings=account.settings,
        )
        return self.insert(chat)
