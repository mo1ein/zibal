from django.conf import settings
from pymongo import MongoClient

_mongo_client = None


def get_mongo_client():
    global _mongo_client
    if _mongo_client is None:
        _mongo_client = MongoClient(settings.MONGO_URI, serverSelectionTimeoutMS=500000)
        print(_mongo_client)
    return _mongo_client


def get_db():
    client = get_mongo_client()
    return client[settings.MONGO_DB_NAME]
