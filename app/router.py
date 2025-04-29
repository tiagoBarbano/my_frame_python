from app.core.routing import post, get
from app.core.application import (
    json_response,
    read_body,
    send_response,
)
from app.user_model import decode

@post("/cotador", summary="Cotador")
async def cotador(scope, receive, send):
    body = await read_body(receive)
    data = decode(body)
    result = {"cotacao_final": data.valor * 1.23, "empresa": data.empresa}
    return await send_response(send, json_response(result))


@get("/", summary="HelloWorld")
async def hello_world(scope, receive, send):
    return await send_response(send, json_response({"message": "HelloWorld"}))
