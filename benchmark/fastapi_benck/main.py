import os
from pydantic import BaseModel
import logging
from fastapi import Body, FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse, ORJSONResponse, Response
import msgspec
import orjson
from fastapi.middleware.gzip import GZipMiddleware

from redis.asyncio import Redis
from pymongo import AsyncMongoClient

import asyncio

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = FastAPI(
    title="",  # evita validações e headers extras
    version="",
    docs_url=None,
    redoc_url=None,
    openapi_url=None,  # desativa geração automática de OpenAPI
)

app.add_middleware(GZipMiddleware, minimum_size=1000)

# --- Redis (async) ---
redis = Redis(
    host="localhost", port=6379, password="redis1234", db=0, decode_responses=True
)
# redis = Redis(host="localhost", port=6379, password="redis1234", db=0, decode_responses=True)

# --- MongoDB (async) ---
mongo_client = AsyncMongoClient(
    "mongodb://localhost:27017",
    maxPoolSize=150,      # ajuste recomendável
    minPoolSize=5,       # mantém conexões prontas
    connectTimeoutMS=500,
    serverSelectionTimeoutMS=500,
    maxConnecting=50,
)
# mongo_client = AsyncMongoClient("mongodb://localhost:27017")

db = mongo_client["cotador"]
collection = db["users"]


@app.on_event("startup")
async def startup_event():
    os.environ["flag_pass"] = "sim"
    try:
        pong = await redis.ping()
        logging.info(f"Redis conectado: {pong}")

        await mongo_client.server_info()  # Falha se não conectar
        logging.info("MongoDB conectado")

    except Exception as e:
        logging.error(f"Erro ao conectar: {str(e)}")


@app.on_event("shutdown")
async def shutdown_event():
    await redis.close()
    await mongo_client.close()


@app.get("/users/{user_id}")
async def mongo_get_id(user_id: str):
    # redis_key = f"user:id:{user_id}"
    # cached = await redis.get(redis_key)
    # if cached:
    #     return msgspec.json.decode(cached)

    logging.info(f"User fetched from MongoDB: {user_id}")
    
    result = await collection.find_one({"_id": user_id})

    if os.environ["flag_pass"] == "sim":
        logging.info(result)
        
    # if not result:
    #     return ORJSONResponse(status_code=404, content={"error": "User not found"})

    # await redis.set(redis_key, msgspec.json.encode(result), ex=60)
    return ORJSONResponse(result)


@app.post("/users")
async def mongo_insert(user: dict = Body()):
    result = await collection.insert_one(user)

    return {"inserted_id": str(result.inserted_id)}


@app.post("/body")
async def root_body(request: Request):
    raw = await request.body()
    body = orjson.loads(memoryview(raw))

    res = await controller_business_manager_rules_handler(body=body)

    return Response(orjson.dumps(res), media_type="application/json")


@app.post("/body-msgspec")
async def root_body_msgspec(request: Request):
    raw = await request.body()
    body = msgspec.json.decode(memoryview(raw))

    res = await controller_business_manager_rules_handler(body=body)

    return Response(msgspec.json.encode(res), media_type="application/json")


async def controller_business_manager_rules_handler(body):
    await asyncio.sleep(0.1)  # Simula operação assíncrona
    return body


@app.get("/json")
async def root():
    return JSONResponse(content={"msg": "Hello World!"})


@app.get("/orjson")
async def root_orjson():
    return ORJSONResponse(content={"msg": "Hello World!"})


@app.get("/msgspec")
async def root_msgspec():
    return Response(
        content=msgspec.json.encode({"msg": "Hello World!"}),
        media_type="application/json",
    )


# Modelo para request
class LogConfig(BaseModel):
    logger_name: str = "root"
    level: str


@app.get("/loggers")
def list_loggers():
    """Retorna todos os loggers e seus níveis atuais."""
    loggers = {}
    for name, logger in logging.Logger.manager.loggerDict.items():
        if isinstance(logger, logging.Logger):
            loggers[name] = logging.getLevelName(logger.level)
    root_level = logging.getLevelName(logging.getLogger().level)
    return {"root": root_level, **loggers}


@app.post("/loggers/update")
def update_logger(config: LogConfig):
    logger_name = config.logger_name

    if logger_name == "root":
        logger = logging.getLogger()
    else:
        logger = logging.getLogger(logger_name)

    level = config.level.upper()

    if level not in logging._nameToLevel:
        raise HTTPException(400, f"Invalid level: {level}")

    # Define o nível do logger
    logger.setLevel(level)

    # MUITO IMPORTANTE: ajusta os handlers também
    for handler in logger.handlers:
        handler.setLevel(level)
        
@app.get("/env")
def list_env():
    return dict(os.environ)

class EnvUpdate(BaseModel):
    key: str
    value: str
    
@app.post("/env/update")
def update_env(data: EnvUpdate):
    os.environ[data.key] = data.value
    return {"message": f"Environment variable '{data.key}' updated", "value": data.value}