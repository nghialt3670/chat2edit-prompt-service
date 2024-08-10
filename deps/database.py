import os

from gridfs import GridFS
from pymongo import MongoClient
from redis import Redis

from db.services import CanvasService, ContextService, ConvService

client = MongoClient(os.getenv("MONGO_URL"))
database = client.get_database(os.getenv("MONGO_DB_NAME"))
redis = Redis(os.getenv("REDIS_HOST"), os.getenv("REDIS_PORT"))

convs = database.get_collection("convs")
canvases = GridFS(database, "files")
contexts = GridFS(database, "contexts")


def get_db():
    return database


def get_conv_service():
    return ConvService(convs, redis)


def get_canvas_service():
    return CanvasService(canvases)


def get_context_service():
    return ContextService(contexts, redis)
