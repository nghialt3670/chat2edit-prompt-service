from typing import List

from pymongo.collection import Collection

from models.db.chat import Chat
from models.db.chat_phase import ChatPhase
from services.document_service import DocumentService


class PhaseService(DocumentService):
    def __init__(self, collection: Collection) -> None:
        super().__init__(collection, ChatPhase)

    def find_by_chat(self, chat: Chat) -> List[ChatPhase]:
        limit = chat.settings.max_chat_phases
        raw_phases = self._collection.find({"chat_id": chat.id}).limit(limit)
        return [ChatPhase.model_validate(phase) for phase in raw_phases]
