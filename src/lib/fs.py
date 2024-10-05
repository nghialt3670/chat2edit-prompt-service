from gridfs import GridFSBucket
from pymongo import MongoClient

from src.utils.env import ENV

client = MongoClient(ENV.MONGO_URI)


def get_bucket(name: str) -> GridFSBucket:
    db = client.get_database()
    return GridFSBucket(db, name)
