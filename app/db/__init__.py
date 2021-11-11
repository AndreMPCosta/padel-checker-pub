from os import environ

from motor.motor_asyncio import AsyncIOMotorClient
from odmantic import AIOEngine

client = AsyncIOMotorClient(f'mongodb://{environ.get("MONGO_USER")}:{environ.get("MONGO_PASSWORD")}'
                            f'@{environ.get("MONGO_HOST")}/admin')
engine = AIOEngine(motor_client=client, database=environ.get("MONGO_DB"))
