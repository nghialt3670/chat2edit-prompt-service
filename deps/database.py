import os

from gridfs import GridFS
from pymongo import MongoClient
from redis import Redis

from db.services import ChatService, ContextService

client = MongoClient(os.getenv("MONGO_URL"))
database = client.get_database(os.getenv("MONGO_DB_NAME"))
redis = Redis(os.getenv("REDIS_HOST"), os.getenv("REDIS_PORT"))

chats = database.get_collection("prompting-chats")
contexts = GridFS(database, "contexts")


def get_db():
    return database


def get_chat_service():
    return ChatService(chats, redis)


def get_context_service():
    return ContextService(contexts, redis)
