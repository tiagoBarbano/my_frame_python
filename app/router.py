import msgspec
import orjson

from urllib.parse import parse_qs

from app.core.routing import post, get
from app.core.application import (
    json_response,
    read_body,
    send_response,
)
from app.infra.database import MongoDB
from app.infra.redis import RedisClient
from app.models.user_model import User, UserDto


@post("/cotador", summary="Cotador")
async def cotador(scope, receive, send):
    body = await read_body(receive)
    data = msgspec.json.decode(body, type=UserDto)
    result = {"cotacao_final": data.valor * 1.23, "empresa": data.empresa}
    user = User.create(**result)
    new_id = await user.save(db=MongoDB.get_db())
    return await send_response(send, json_response({"id": str(new_id.inserted_id)}))


@get("/cotador", summary="Cotador Get")
async def cotador_get(scope, receive, send):
    query = parse_qs(scope.get("query_string", b"").decode())
    id = query.get("id", [None])[0]
    
    key_redis = f"cotador:{id}"
    redis_client = RedisClient.get()
    cached_result = await redis_client.get(key_redis)
    
    if cached_result:
        return await send_response(send, json_response(orjson.loads(cached_result)))
    
    result = await User.find_by_id(id=id, db=MongoDB.get_db())

    if not result:
        return await send_response(send, json_response("Recurso não encontrado", 404))

    await redis_client.set(key_redis, orjson.dumps(result), ex=1)
    return await send_response(send, json_response(result))


@get("/cotadores", summary="Cotador Get ALL")
async def cotador_get_all(scope, receive, send):
    result: list = await User.find_all(db=MongoDB.get_db())

    if not result:
        return await send_response(send, json_response("Recurso não encontrado", 404))

    return await send_response(send, json_response(result))


@get("/", summary="HelloWorld")
async def hello_world(scope, receive, send):
    return await send_response(send, json_response({"message": "HelloWorld"}))
