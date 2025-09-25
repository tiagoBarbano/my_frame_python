import msgspec
import time

from jsonschema import ValidationError

from app.core.exception import AppException
from app.core.params import HeaderParams, QueryParams, PathParams
from app.core.routing import post, get
from app.core.utils import (
    response,
    get_query_param,
    read_body,
    validate_schema,
)
from app.dto.user_dto import UserListResponse, UserRequestDto, UserResponseDto
from app.services.user_service import UserService
from app.core.logger import log  # noqa: F401

user_service = UserService()


@post(
    "/users",
    summary="Users",
    description="EndPoint responsável por cadastrar usuarios",
    request_model=UserRequestDto,
    response_model=UserResponseDto,
    headers=[
        HeaderParams(name="X-Token", type_field="string", description="Token de acesso")
    ],
    tags=["USERS"],
)
async def users(scope, receive, send):
    try:
        body = await read_body(receive)
        data = await validate_schema(body, UserRequestDto, return_dict=False)

        new_user = await user_service.create_user(data)

        return await response(send, new_user)
    except (msgspec.ValidationError, ValueError, TypeError, ValidationError) as e:
        log.error(f"Validation error: {e.args[0]}")
        return await response(send, {"error": e.args[0]}, status=422)
    except Exception as e:  # noqa: B902
        log.error(f"Unexpected error: {e}")
        return await response(send, {"error": str(e)}, status=500)


@get(
    "/users",
    summary="Users Get",
    tags=["USERS"],
    response_model=UserResponseDto,
    query_params=[
        QueryParams(
            name="id", type_field="string", required=True, description="id do cliente"
        )
    ],
)
async def users_get(scope, receive, send):
    start_process = time.perf_counter()

    _id = get_query_param(scope=scope, name="id", default=None, cast=str)

    user_result = await user_service.get_user_by_id(user_id=_id)

    if not user_result:
        return await response(send, "recurso nao encontrado", status=404)

    time_process = time.perf_counter() - start_process
    return await response(send, user_result, headers={"time_process": f"{time_process:.7f} segs"})


@get(
    "/users/{id}",
    summary="Users Get",
    tags=["USERS"],
    response_model=UserResponseDto,
    path_params=[
        PathParams(
            name="id", type_field="string", required=True, description="id do cliente"
        ),
    ],
)
async def user_ges_path(scope, receive, send):
    user_result = await user_service.get_user_by_id(user_id=scope["path_params"]["id"])

    return await response(send, user_result)


@get(
    "/users_all",
    summary="Users Get ALL",
    tags=["USERS"],
    response_model=UserListResponse,
    query_params=[
        QueryParams(name="page", required=True, type_field="integer", default=1),
        QueryParams(name="limite", required=True, type_field="integer", default=10),
    ],
)
async def users_get_all(scope, receive, send) -> list[dict]:
    page = get_query_param(scope, "page", 1, int)
    limit = get_query_param(scope, "limite", 10, int)
    result = await user_service.list_users(page=page, limit=limit)
    return await response(send, result)


@get("/", summary="HelloWorld", tags=["helloWorld"])
async def hello_world(scope, receive, send):
    return await response(send, {"message": "HelloWorld"})


@get("/exception", summary="Exception", tags=["helloWorld"])
async def exception(scope, receive, send):
    raise AppException(
        {
            "error": "Erro de teste",
            "error_detail": "Teste para avaliar a classe de erro genérica",
        },
        status_code=500,
    )
