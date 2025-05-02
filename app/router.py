from app.core.exception import AppException
from app.core.routing import post, get
from app.core.application import (
    json_response,
    read_body,
    send_response,
)
from app.infra.database import MongoDB
from app.models.user_model import User, decode




@post("/cotador", summary="Cotador")
async def cotador(scope, receive, send):
    db = MongoDB.get_db()
    body = await read_body(receive)
    data = decode(body)
    result = {"cotacao_final": data.valor * 1.23, "empresa": data.empresa}
    user = User(result)
    res_insert = await db["cotador"].insert_one(result)
    return await send_response(send, json_response(result))


@get("/", summary="HelloWorld")
async def hello_world(scope, receive, send):
    return await send_response(send, json_response({"message": "HelloWorld"}))

@get("/exception", summary="HelloWorld")
async def exception_handler(scope, receive, send):
    raise AppException("Recurso não encontrado", 400)
