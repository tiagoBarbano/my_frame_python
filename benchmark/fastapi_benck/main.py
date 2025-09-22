from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
import anyio
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app):
    limiter = anyio.to_thread.current_default_thread_limiter()
    limiter.total_tokens = 1000
    yield

app = FastAPI(lifespan=lifespan)


@app.get("/")
async def root():
    return ORJSONResponse(content={"msg": "Hello World!"})
