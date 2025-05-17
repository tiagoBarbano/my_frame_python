# from opentelemetry.instrumentation.pymongo import PymongoInstrumentor
from pymongo import AsyncMongoClient
from pymongo.errors import ConfigurationError, ConnectionFailure, OperationFailure
from contextlib import asynccontextmanager

from app.core.logger import log
from app.config import get_settings

settings = get_settings()

# PymongoInstrumentor().instrument()

class MongoManager:
    _client = None

    @classmethod
    def get_client(cls):
        if cls._client is None:
            cls._client = AsyncMongoClient(settings.mongo_url)
        return cls._client

    @classmethod
    @asynccontextmanager
    async def get_database(cls):
        client = cls.get_client()
        try:
            db = client[settings.mongo_db]
            yield db
        except(ConnectionFailure, ConfigurationError, OperationFailure) as ex:
            client.close()
            log.error(f"MongoDB connection error: {ex}")
            raise