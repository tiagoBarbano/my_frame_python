import msgspec
import time

from jsonschema import ValidationError
from urllib.parse import parse_qs

from app.core.exception import AppException
from app.core.params import HeaderParams, QueryParams, PathParams
from app.core.routing import post, get
from app.core.utils import (
    json_response,
    read_body,
    send_response,
    validate_schema_dict,
)
from app.dto.user_dto import CotadorListResponse, UserRequestDto, UserResponseDto
from app.models.user_model import UserModel
from app.services.user_service import UserService
from app.core.logger import log  # noqa: F401

user_service = UserService()


@post(
    "/cotador",
    summary="Cotador",
    description="EndPoint responsável por cadastrar cotacoes",
    request_model=UserRequestDto,
    response_model=UserResponseDto,
    headers=[
        HeaderParams(name="X-Token", type_field="string", description="Token de acesso")
    ],
    tags=["cotador"],
)
async def cotador(scope, receive, send):
    try:
        body = await read_body(receive)

        data = await validate_schema_dict(body, UserRequestDto)

        new_user = await user_service.create_user(data)

        return await send_response(send, json_response(new_user))
    except (msgspec.ValidationError, ValueError, TypeError, ValidationError) as e:
        log.error(f"Validation error: {e.args[0]}")
        return await send_response(
            send, json_response({"error": e.args[0]}, status=422)
        )
    except Exception as e:  # noqa: B902
        log.error(f"Unexpected error: {e}")
        return await send_response(send, json_response({"error": str(e)}, status=500))


@get(
    "/user",
    summary="Cotador Get",
    tags=["cotador"],
    response_model=UserResponseDto,
    query_params=[
        QueryParams(
            name="id", type_field="string", required=True, description="id do cliente"
        )
    ],
)
async def cotador_get(scope, receive, send):
    start_process = time.perf_counter()

    query = parse_qs(scope.get("query_string", b"").decode())
    _id = query.get("id", [None])[0]

    user_result = await user_service.get_user_by_id(user_id=_id)

    if not user_result:
        return await send_response(send, json_response("Recurso não encontrado", 404))

    time_process = time.perf_counter() - start_process
    return await send_response(
        send,
        json_response(
            user_result, headers={"time_process": f"{time_process:.7f} segs"}
        ),
    )


@get(
    "/user/{id}",
    summary="Cotador Get",
    tags=["cotador"],
    response_model=UserModel,
    path_params=[
        PathParams(
            name="id", type_field="string", required=True, description="id do cliente"
        ),
    ],
)
async def cotador_gest(scope, receive, send):
    item_id = scope["path_params"]["id"]

    user_result = await user_service.get_user_by_id(user_id=item_id)

    if not user_result:
        return await send_response(send, json_response("Recurso não encontrado", 404))

    return await send_response(send, json_response(user_result))


@get(
    "/cotadores",
    summary="Cotador Get ALL",
    tags=["cotador"],
    response_model=CotadorListResponse,
    query_params=[
        QueryParams(name="page", required=True, type_field="integer", default=1),
        QueryParams(name="limite", required=True, type_field="integer", default=10),
    ],
)
async def cotador_get_all(scope, receive, send) -> list[dict]:
    query = parse_qs(scope.get("query_string", b"").decode())
    page = int(query.get("page", ["1"])[0])
    limit = int(query.get("limite", ["10"])[0])

    result = await user_service.list_users(page=page, limit=limit)
    return await send_response(send, json_response(result))


@get("/", summary="HelloWorld", tags=["helloWorld"])
async def hello_world(scope, receive, send):
    return await send_response(send, json_response({"message": "HelloWorld"}))


@get("/exception", summary="Exception", tags=["helloWorld"])
async def exception(scope, receive, send):
    raise AppException(
        {
            "error": "Erro de teste",
            "error_detail": "Teste para avaliar a classe de erro genérica",
        },
        status_code=500,
    )
