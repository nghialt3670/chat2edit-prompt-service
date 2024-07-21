import os

from gridfs import GridFS
from pymongo import MongoClient
from redis import Redis

from database.services import ConvService, UserService
from database.services.canvas_service import CanvasService
from database.services.context_service import ContextService

client = MongoClient(os.getenv("MONGO_URL"))
database = client.get_database("chat2edit")
redis = Redis(os.getenv("REDIS_HOST"), os.getenv("REDIS_PORT"))

convs = database.get_collection("convs")
users = database.get_collection("users")
canvases = GridFS(database, "canvases")
contexts = GridFS(database, "contexts")


def get_conv_service():
    return ConvService(convs, redis)


def get_user_service():
    return UserService(users)


def get_canvas_service():
    return CanvasService(canvases)


def get_context_service():
    return ContextService(contexts, redis)
