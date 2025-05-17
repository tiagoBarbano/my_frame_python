import asyncio
from app.core.logger import _log_writer

from app.infra.database import MongoManager
from app.infra.redis import RedisClient


def startup():
    """Startup middleware for initializing resources."""
    asyncio.create_task(_log_writer())
    RedisClient.init()
    MongoManager.init_client("mongodb://localhost:27017")


async def lifespan(scope, receive, send):
    """Lifespan middleware for startup and shutdown events."""
    msg = await receive()
    if msg["type"] == "lifespan.startup":
        startup()
        await send({"type": "lifespan.startup.complete"})

