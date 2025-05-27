import asyncio
from app.core.logger import _log_writer, _shutdown_logging

from app.infra.proxy_handler import SessionManager
from app.infra.redis import RedisClient
from app.infra.database import MongoManager


async def startup() -> None:
    """Startup middleware for initializing resources."""
    asyncio.create_task(_log_writer())
    RedisClient.init()
    MongoManager.init()
    SessionManager().init()


async def shutdown() -> None:
    """Shutdown middleware for cleaning up resources."""
    await RedisClient.close()
    await MongoManager.close()
    await SessionManager.close_session()
    await _shutdown_logging()


async def lifespan(scope, receive, send) -> None:
    while True:
        """Lifespan middleware for startup and shutdown events."""
        msg = await receive()
        if msg["type"] == "lifespan.startup":
            await startup()
            await send({"type": "lifespan.startup.complete"})
        elif msg["type"] == "lifespan.shutdown":
            await shutdown()
            await send({"type": "lifespan.shutdown.complete"})
            return
