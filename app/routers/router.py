from urllib.parse import parse_qs

import msgspec
import orjson

from app.core.routing import post, get
from app.core.application import (
    json_response,
    read_body,
    send_response,
)
from app.models.user_model import UserDto, validate_all_fields
from app.services.user_service import UserService
from app.core.logger import log  # noqa: F401

user_service = UserService()


@post(
    "/cotador",
    summary="Cotador",
    description="EndPoint responsável por cadastrar cotacoes",
    request_model=UserDto,
    response_model=UserDto,
    headers=[
        {"name": "X-Token", "type": "string", "description": "Token de acesso"},
        {"name": "X-Customer-Id", "type": "integer", "description": "ID do cliente"}
    ]    
)
async def cotador(scope, receive, send):
    try:
        body = await read_body(receive)
        data = validate_all_fields(orjson.loads(body), UserDto)

        # new_user = await user_service.create_user(data)
        if not msgspec.json.decode(orjson.dumps(data), type=UserDto):
            raise ValueError("Invalid data")

        return await send_response(send, json_response(data))
    except (msgspec.ValidationError, ValueError) as e:
        log.error(f"Validation error: {e}")
        return await send_response(
            send, json_response({"error": e.args[0]}, status=422)
        )
    except Exception as e:  # noqa: B902
        log.error(f"Unexpected error: {e}")
        return await send_response(send, json_response({"error": str(e)}, status=500))


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


@get("/schema", summary="Schema", request_model=UserDto, response_model=UserDto)
async def teste_schema(scope, receive, send):
    schema = msgspec.json.schema(list[UserDto])
    schema_components = msgspec.json.schema_components(list[UserDto])

    # Print out that schema as JSON
    print(schema_components)
    return await send_response(send, json_response(schema))
