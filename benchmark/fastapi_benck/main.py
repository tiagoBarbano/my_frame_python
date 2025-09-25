from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI(
    title="FastAPI Benchmark",
    version="1.0.0",
    default_response_class=ORJSONResponse,
    lifespan=None,
    docs_url=None,
    redoc_url=None,
    
)
Instrumentator().instrument(app).expose(app, should_gzip=True, include_in_schema=False)


@app.get("/")
async def root():
    return ORJSONResponse(content={"msg": "Hello World!"})
