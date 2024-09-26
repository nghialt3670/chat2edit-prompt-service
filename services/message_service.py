from typing import List

from pymongo.collection import Collection

from models.db.chat import Chat
from models.db.message import Message
from services.document_service import DocumentService


class MessageService(DocumentService):
    def __init__(self, collection: Collection) -> None:
        super().__init__(collection, Message)

    def find_by_chat(self, chat: Chat) -> List[Message]:
        raw_messages = self._collection.find({"chat_id": chat.id})
        return [Message.model_validate(msg) for msg in raw_messages]

    def save(self, message: Message) -> None:
        self.insert_and_assign_id(message)
