from collections import defaultdict
import msgspec
from app.config import Settings
from app.core._utils import compile_path_to_regex
from app.core.params import HeaderParams, PathParams, QueryParams

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
                    parameters.append(
                        {
                            "name": header.name,
                            "in": header._in,
                            "required": header.required,
                            "schema": {"type": header.type_field},
                            "description": header.description,
                        }
                    )

            if query_params:
                for q_param in query_params:
                    parameters.append(
                        {
                            "name": q_param.name,
                            "in": q_param._in,
                            "required": q_param.required,
                            "schema": {"type": q_param.type_field},
                            "description": q_param.description,
                        }
                    )

            if path_params:
                for p_param in path_params:
                    parameters.append(
                        {
                            "name": p_param.name,
                            "in": p_param._in,
                            "required": p_param.required,
                            "schema": {"type": p_param.type_field},
                            "description": p_param.description,
                        }
                    )

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
    path_params=None: route(
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
    path_params=None: route(
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
    )
)
