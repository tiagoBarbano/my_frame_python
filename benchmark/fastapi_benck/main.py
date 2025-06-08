from fastapi import FastAPI, Request
from fastapi.responses import ORJSONResponse

app = FastAPI(
    debug=False,
    include_in_schema=False,
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)


@app.get("/")
async def root(request: Request):
    return ORJSONResponse(content={"message": "Hello World"})
