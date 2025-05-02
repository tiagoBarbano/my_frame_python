
import redis.asyncio as redis

from opentelemetry.instrumentation.redis import RedisInstrumentor

RedisInstrumentor().instrument()


class RedisClient:
    _client: redis.Redis | None = None

    @classmethod
    def init(cls, url: str = "redis://localhost:6379", **kwargs):
        if cls._client is None:
            cls._client = redis.from_url(url, decode_responses=True, **kwargs)

    @classmethod
    def get(cls) -> redis.Redis:
        if cls._client is None:
            raise RuntimeError("Redis client not initialized. Call RedisClient.init() first.")
        return cls._client

    @classmethod
    async def close(cls):
        if cls._client:
            await cls._client.close()
            cls._client = None
