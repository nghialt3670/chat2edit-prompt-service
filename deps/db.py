from gridfs import GridFSBucket
from pymongo import MongoClient

from services.account_service import AccountService
from services.chat_service import ChatService
from services.context_service import ContextService
from services.message_service import MessageService
from services.phase_service import PhaseService
from utils.env import ENV

client = MongoClient(ENV.MONGO_URI)
db = client.get_default_database()


def get_account_service():
    collection = db.get_collection("accounts")
    return AccountService(collection)


def get_chat_service():
    collection = db.get_collection("chats")
    return ChatService(collection)


def get_phase_service():
    collection = db.get_collection("chat-phases")
    return PhaseService(collection)


def get_context_service():
    collection = db.get_collection("contexts")
    bucket = GridFSBucket(db, "contexts")
    return ContextService(collection, bucket)


def get_message_service():
    collection = db.get_collection("messages")
    return MessageService(collection)
