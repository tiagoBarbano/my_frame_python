from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, ORJSONResponse, Response
import msgspec
import orjson
from fastapi.middleware.gzip import GZipMiddleware

app = FastAPI(
    title="",  # evita validações e headers extras
    version="",
    lifespan=None,
    docs_url=None,
    redoc_url=None,
    openapi_url=None,  # desativa geração automática de OpenAPI
)

app.add_middleware(GZipMiddleware, minimum_size=1000)

@app.post("/body")
async def root_body(request: Request):    
    raw = await request.body()
    body = orjson.loads(memoryview(raw))

    res = controller_business_manager_rules_handler(body=body)

    return Response(orjson.dumps(res), media_type="application/json")

@app.post("/body-msgspec")
async def root_body_msgspec(request: Request):    
    raw = await request.body()
    body = msgspec.json.decode(raw)

    res = controller_business_manager_rules_handler(body=body)
    encoded = msgspec.json.encode(res)

    # Reaproveita o buffer, evita revalidação de headers
    return Response(encoded, media_type="application/json")


def controller_business_manager_rules_handler(body):
    return body


@app.get("/json")
async def root():
    return JSONResponse(content={"msg": "Hello World!"})


@app.get("/orjson")
async def root_orjson():
    return ORJSONResponse(content={"msg": "Hello World!"})

@app.get("/msgspec")
async def root_msgspec():
    return Response(content=msgspec.json.encode({"msg":"Hello World!"}), media_type="application/json")
