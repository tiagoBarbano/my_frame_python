from urllib.parse import parse_qs

import msgspec

from app.core.routing import post, get
from app.core.application import (
    json_response,
    read_body,
    send_response,
)
from app.models.user_model import UserDto
from app.services.user_service import UserService

user_service = UserService()


@post("/cotador", summary="Cotador")
async def cotador(scope, receive, send):
    body = await read_body(receive)
    data = msgspec.json.decode(body, type=UserDto)
    
    new_user = await user_service.create_user(data)

    return await send_response(send, json_response({"user": new_user}))


@get("/cotador", summary="Cotador Get")
async def cotador_get(scope, receive, send):
    query = parse_qs(scope.get("query_string", b"").decode())
    id = query.get("id", [None])[0]

    user_result = await user_service.get_user_by_id(user_id=id)

    if not user_result:
        return await send_response(send, json_response("Recurso não encontrado", 404))

    return await send_response(send, json_response(user_result))


@get("/cotadores", summary="Cotador Get ALL")
async def cotador_get_all(scope, receive, send) -> list[dict]:
    result = await user_service.list_users()
    return await send_response(send, json_response(result))


@get("/", summary="HelloWorld")
async def hello_world(scope, receive, send):
    return await send_response(send, json_response({"message": "HelloWorld"}))
