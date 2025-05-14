from collections import defaultdict
import msgspec
from app.config import Settings
from app.core._utils import compile_path_to_regex
from app.core.params import HeaderParams, PathParams, QueryParams, CookieParams

settings = Settings()
routes = []
routes_by_method = defaultdict(list)

openapi_spec = {
    "openapi": "3.0.0",
    "info": {"title": settings.app_name, "version": "1.0.0"},
    "paths": {},
    "components": {"schemas": {}},
}


def route(
    method: str,
    path: str,
    summary: str = "",
    description: str = None,
    request_model=None,
    response_model=None,
    headers: list[HeaderParams] = None,
    tags: list[str] = None,
    query_params: list[QueryParams] = None,
    path_params: list[PathParams] = None,
    cookie_params: list[CookieParams] = None,
):
    def decorator(func):
        if settings.enable_swagger:
            request_content = None
            response_content = None

            if response_model:
                schema = msgspec.json.schema(response_model)
                schemas = openapi_spec["components"]["schemas"]

                model_name = response_model.__name__
                schemas[model_name] = schema["$defs"][model_name]

                response_content = {
                    "application/json": {
                        "schema": {"$ref": f"#/components/schemas/{model_name}"}
                    }
                }

            if request_model:
                request_schema = msgspec.json.schema(request_model)
                request_schemas = openapi_spec["components"]["schemas"]

                request_model_name = request_model.__name__
                request_schemas[request_model_name] = request_schema["$defs"][
                    request_model_name
                ]

                request_content = {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": f"#/components/schemas/{request_model_name}"
                            }
                        }
                    },
                }

            parameters = []

            if headers:
                for header in headers:
                    parameters.append(header.encode_dict())

            if query_params:
                for q_param in query_params:
                    parameters.append(q_param.encode_dict())

            if path_params:
                for p_param in path_params:
                    parameters.append(p_param.encode_dict())

            if cookie_params:
                for p_param in path_params:
                    parameters.append(p_param.encode_dict())                    

            openapi_spec["paths"].setdefault(path, {})[method] = {
                "summary": summary,
                "tags": tags,
                "description": description,
                "parameters": parameters,
                "requestBody": request_content,
                "responses": {
                    "200": {
                        "description": "Sucesso",
                        "content": response_content,
                    },
                    "422": {
                        "description": "Validation Error",
                        "content": {"application/json": {}},
                    },
                },
            }

        regex_pattern = compile_path_to_regex(path)
        routes.append((regex_pattern, path, method.upper(), func))
        routes_by_method[method.upper()].append((regex_pattern, path, func))
        # routes[(regex_pattern, path, method.upper())] = func
        return func

    return decorator


# Atalhos para GET e POST
get = (  # noqa: E731
    lambda path,
    summary,
    description=None,
    request_model=None,
    response_model=None,
    headers=None,
    tags=None,
    query_params=None,
    path_params=None,
    cookie_params=None: route(
        "get",
        path,
        summary,
        description,
        request_model,
        response_model,
        headers,
        tags,
        query_params,
        path_params,
        cookie_params,
    )
)
post = (  # noqa: E731
    lambda path,
    summary,
    description=None,
    request_model=None,
    response_model=None,
    headers=None,
    tags=None,
    query_params=None,
    path_params=None,
    cookie_params=None: route(
        "post",
        path,
        summary,
        description,
        request_model,
        response_model,
        headers,
        tags,
        query_params,
        path_params,
        cookie_params,
    )
)
