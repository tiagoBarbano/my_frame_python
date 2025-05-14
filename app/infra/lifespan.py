from app.infra.database import MongoDB
from app.infra.redis import RedisClient


def startup():
    """Startup middleware for initializing resources."""
    RedisClient.init()
    MongoDB.init()


def shutdown():
    """Shutdown middleware for cleaning up resources."""
    RedisClient.close()
    MongoDB.close()


async def lifespan(scope, receive, send):
    """Lifespan middleware for startup and shutdown events."""
    msg = await receive()
    if msg["type"] == "lifespan.startup":
        startup()
        await send({"type": "lifespan.startup.complete"})
    elif msg["type"] == "lifespan.shutdown":
        shutdown()
        print("Shutting down...")
        await send({"type": "lifespan.shutdown.complete"})
