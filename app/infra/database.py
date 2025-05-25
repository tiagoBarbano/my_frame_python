from opentelemetry.instrumentation.pymongo import PymongoInstrumentor
from pymongo import AsyncMongoClient
from pymongo.errors import ConfigurationError, ConnectionFailure, OperationFailure
from contextlib import asynccontextmanager

from app.core.logger import log
from app.config import get_settings

settings = get_settings()

PymongoInstrumentor().instrument()


class MongoManager:
    """Manages the MongoDB client connection for the application.

    Provides methods to obtain and close the MongoDB client and database connections.
    """
    _client: AsyncMongoClient | None = None

    @classmethod
    def init(cls):
        """Inicializa o client dentro do loop correto."""
        cls._client = AsyncMongoClient(
                settings.mongo_url,
                maxPoolSize=1500,  # aumenta a concorrência com o Mongo
                minPoolSize=100,
                serverSelectionTimeoutMS=3000,
                socketTimeoutMS=5000,
            )

    @classmethod
    def get_client(cls):
        if cls._client is None:
            raise RuntimeError("Mongo client not initialized. Call MongoManager.init() first.")
        return cls._client

    @classmethod
    @asynccontextmanager
    async def get_database(cls):
        client = cls.get_client()
        try:
            yield client[settings.mongo_db]
        except (ConnectionFailure, ConfigurationError, OperationFailure) as ex:
            client.close()
            log.error(f"MongoDB connection error: {ex}")
            raise

    @classmethod
    async def close(cls):
        if cls._client:
            await cls._client.close()
            cls._client = None
            log.info("MongoDB connection closed.")
        else:
            log.warning("MongoDB client is already closed.")