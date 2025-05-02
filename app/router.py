import msgspec

from urllib.parse import parse_qs

from app.core.exception import AppException
from app.core.routing import post, get
from app.core.application import (
    json_response,
    read_body,
    send_response,
)
from app.infra.database import MongoDB
from app.models.user_model import User, UserDto


@post("/cotador", summary="Cotador")
async def cotador(scope, receive, send):
    db = MongoDB.get_db()
    body = await read_body(receive)
    data = msgspec.json.decode(body, type=UserDto)
    result = {"cotacao_final": data.valor * 1.23, "empresa": data.empresa}
    user = User.create(**result)
    new_id = await user.save(db)
    return await send_response(send, json_response({"id": str(new_id.inserted_id)}))


@get("/cotador", summary="Cotador Get")
async def cotador_get(scope, receive, send):
    query = parse_qs(scope.get("query_string", b"").decode())
    id = query.get("id", [None])[0]
    
    result_mongo = await User.find_by_id(id=id, db=MongoDB.get_db())
    
    if not result_mongo:
        raise AppException("Recurso não encontrado", 404)
    
    result = await User.mongo_to_model(result_mongo)
    return await send_response(send, json_response(result.to_dict()))


@get("/", summary="HelloWorld")
async def hello_world(scope, receive, send):
    return await send_response(send, json_response({"message": "HelloWorld"}))

