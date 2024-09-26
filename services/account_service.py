from typing import Optional, Union

from bson import ObjectId
from pymongo.collection import Collection

from models.db.account import Account
from services.document_service import DocumentService


class AccountService(DocumentService):
    def __init__(self, collection: Collection) -> None:
        super().__init__(collection, Account)

    def create_with_id(self, id: Union[str, ObjectId]) -> Account:
        account = Account(id=id)
        self.insert_with_id(account)
        return account
