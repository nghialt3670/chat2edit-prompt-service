import os

from gridfs import GridFS
from pymongo import MongoClient
from redis import Redis

from database.services import ConvService, UserService
from database.services.file_service import FileService

client = MongoClient(os.getenv("MONGO_URL"))
database = client.get_database("chat2edit")
redis = Redis(os.getenv("REDIS_HOST"), os.getenv("REDIS_PORT"))


convs = database.get_collection("convs")
users = database.get_collection("users")
gridfs = GridFS(database, "files")


def get_conv_service():
    return ConvService(convs, redis)


def get_user_service():
    return UserService(users)


def get_file_service():
    return FileService(gridfs)
