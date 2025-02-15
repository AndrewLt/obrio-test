from motor.motor_asyncio import AsyncIOMotorClient
from backend.configs import settings

client = AsyncIOMotorClient(host=settings.MONGO_HOST, port=settings.MONGO_PORT)

tasks_collection = client.obrio.appReviews

# indexing
tasks_collection.create_index([("appId", 1), ("reviewDate", -1)])
