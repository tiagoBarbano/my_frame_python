import asyncio
from app.core.logger import _log_writer

from app.infra.redis import RedisClient
from app.infra.database import MongoManager


async def startup():
    """Startup middleware for initializing resources."""
    asyncio.create_task(_log_writer())
    RedisClient.init()


async def shutdown():
    """Shutdown middleware for cleaning up resources."""
    RedisClient.close()
    MongoManager.close()



async def lifespan(scope, receive, send):
    """Lifespan middleware for startup and shutdown events."""
    msg = await receive()
    if msg["type"] == "lifespan.startup":
        await startup()
        await send({"type": "lifespan.startup.complete"})

