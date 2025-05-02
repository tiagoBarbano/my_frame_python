from motor.motor_asyncio import AsyncIOMotorClient
from opentelemetry.instrumentation.pymongo import PymongoInstrumentor

from app.config import get_settings

settings = get_settings()

PymongoInstrumentor().instrument()


class MongoDB:
    _client: AsyncIOMotorClient | None = None

    @classmethod
    def init(cls):
        if cls._client is None:
            cls._client = AsyncIOMotorClient(settings.mongo_url)
        cls._db = cls._client[settings.mongo_db]

    @classmethod
    def get_db(cls):
        if cls._client is None:
            raise RuntimeError(
                "MongoDB client not initialized. Call MongoDB.init first."
            )
        return cls._db

    @classmethod
    def close(cls):
        cls._client.close()
