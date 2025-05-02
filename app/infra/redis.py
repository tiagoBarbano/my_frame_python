import redis.asyncio as redis

from opentelemetry.instrumentation.redis import RedisInstrumentor

from app.config import get_settings


settings = get_settings()

RedisInstrumentor().instrument()


class RedisClient:
    _client: redis.Redis | None = None

    @classmethod
    def init(cls):
        if cls._client is None:
            cls._client = redis.from_url(settings.redis_url, decode_responses=True)

    @classmethod
    def get(cls) -> redis.Redis:
        if cls._client is None:
            raise RuntimeError(
                "Redis client not initialized. Call RedisClient.init() first."
            )
        return cls._client

    @classmethod
    async def close(cls):
        if cls._client:
            await cls._client.close()
            cls._client = None
