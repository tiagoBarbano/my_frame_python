from dataclasses import dataclass
import functools
import hashlib
import inspect
import zlib
import orjson
from typing import Callable, Any, Optional
from redis.exceptions import RedisError
from contextlib import asynccontextmanager
import redis.asyncio as redis
from opentelemetry.instrumentation.redis import RedisInstrumentor

from app.config import get_settings
from app.core.logger import log


settings = get_settings()

RedisInstrumentor().instrument(
    command_list_hook=lambda cmd: log.debug(f"Redis command: {cmd}")
)


@dataclass(slots=True)
class RedisClient:
    _pool: redis.ConnectionPool | None = None
    _client: redis.Redis | None = None

    @classmethod
    def init(cls):
        """Inicializa o client dentro do loop correto."""
        cls._pool = redis.ConnectionPool.from_url(
            settings.redis_url,
            max_connections=500,
            socket_timeout=2,  # tempo para operações
            socket_connect_timeout=2,  # tempo para conectar
            retry_on_timeout=True,
        )
        cls._client = redis.Redis(connection_pool=cls._pool, decode_responses=False)

    @classmethod
    def get(cls) -> redis.Redis:
        if cls._client is None:
            raise RuntimeError(
                "Redis client not initialized. Call RedisClient.init() first."
            )
        return cls._client

    @classmethod
    @asynccontextmanager
    async def connection(cls):
        client = cls.get()
        try:
            yield client
        finally:
            pass  # não fecha aqui, pois o client é singleton

    @classmethod
    async def close(cls):
        if cls._client:
            await cls._client.close()
            cls._client = None
            log.info("Redis connection closed.")


def compress(data: bytes) -> bytes:
    return zlib.compress(data, level=3)


def decompress(data: bytes) -> bytes:
    return zlib.decompress(data)


def redis_cache(
    ttl: int = 60,
    key_prefix: str = "cache",
    key_fn: Optional[Callable[..., str]] = None,
    use_cache: bool = True,
):
    """
    Decorador assíncrono que cacheia a resposta da função usando Redis.

    Parâmetros:
    - ttl: tempo em segundos para manter o cache (default: 60)
    - key_prefix: prefixo da chave no Redis
    - key_fn: função opcional para gerar a chave de cache personalizada
            exemplo: key_fn=lambda user_id, **_: f"id:{user_id}"
    """

    def decorator(func: Callable):
        sig = inspect.signature(func)

        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            if not use_cache:
                return await func(*args, **kwargs)

            try:
                bound = sig.bind(*args, **kwargs)
                bound.apply_defaults()
                arguments = bound.arguments

                if key_fn:
                    redis_key = f"{key_prefix}:{key_fn(**arguments)}"
                else:
                    key_raw = f"{func.__module__}.{func.__name__}:{arguments}:{kwargs}"
                    key_hash = hashlib.sha256(key_raw.encode()).hexdigest()
                    redis_key = f"{key_prefix}:{key_hash}"

                async with RedisClient.connection() as redis:
                    cached = await redis.get(redis_key)
                    if cached:
                        return orjson.loads(cached)

                    result = await func(*args, **kwargs)

                    if result is not None:
                        await redis.set(redis_key, orjson.dumps(result), ex=ttl)

                    return result

            except RedisError as e:
                log.error(str(e), stack_info=True)
                return await func(*args, **kwargs)

        return wrapper

    return decorator
