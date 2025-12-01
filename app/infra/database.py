from pymongo import AsyncMongoClient
from app.config import get_settings
from app.core.logger import log

settings = get_settings()


class MongoManager:
    _client: AsyncMongoClient | None = None

    @classmethod
    def init(cls):
        if cls._client is None:
            cls._client = AsyncMongoClient(
                settings.mongo_url,
                maxPoolSize=150,      # ajuste recomendável
                minPoolSize=5,       # mantém conexões prontas
                connectTimeoutMS=500,
                serverSelectionTimeoutMS=500,
                maxConnecting=50,
            )
            log.info("MongoDB client initialized")

    @classmethod
    def get_client(cls):
        if cls._client is None:
            raise RuntimeError("Mongo client not initialized.")
        return cls._client

    @classmethod
    def get_database(cls):
        """Fast access without context manager."""
        return cls.get_client()[settings.mongo_db]

    @classmethod
    async def close(cls):
        if cls._client:
            cls._client.close()
            cls._client = None
            log.info("MongoDB client closed")
