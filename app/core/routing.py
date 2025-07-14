import msgspec

from collections import defaultdict
from typing import Tuple, Type
from app.config import Settings
from app.core.exception import ErrorResponse, ErrorResponseGeneric
from app.core.utils import compile_path_to_regex
from app.core.params import HeaderParams, PathParams, QueryParams, CookieParams

settings = Settings()
routes = {}
routes_by_method = defaultdict(list)

openapi_spec = {
    "openapi": "3.0.0",
    "info": {"title": settings.app_name, "version": "1.0.0"},
    "paths": {},
    "components": {"schemas": {}},
}


def encode_dict(model) -> dict:
    schema = {"type": model.type_field}

    if model.description:
        schema["description"] = model.description
    if model.enum:
        schema["enum"] = model.enum
    if model.pattern:
        schema["pattern"] = model.pattern
    if model.example is not None:
        schema["example"] = model.example
    if model.maxLength is not None:
        schema["maxLength"] = model.maxLength
    if model.minLength is not None:
        schema["minLength"] = model.minLength
    if model.default is not None:
        schema["default"] = model.default

    return {
        "name": model.name,
        "in": model._in,
        "required": model.required,
        "schema": schema,
        "deprecated": model.deprecated,
        "allowEmptyValue": model.allow_empty_value,
    }


def convert_msgspec_schema_to_openapi(
    struct_type: Type[msgspec.Struct],
) -> Tuple[dict, dict]:
    """Adapta JSON Schema do msgspec para formato do OpenAPI."""
    raw_schema = msgspec.json.schema(struct_type)

    # Extrai todos os modelos ($defs)
    defs = raw_schema.pop("$defs", {})

    # Corrige os $ref
    def fix_refs(obj):
        if isinstance(obj, dict):
            for k, v in obj.items():
                if k == "$ref" and isinstance(v, str) and v.startswith("#/$defs/"):
                    obj[k] = v.replace("#/$defs/", "#/components/schemas/")
                else:
                    fix_refs(v)
        elif isinstance(obj, list):
            for item in obj:
                fix_refs(item)

    # Modelo principal como referência
    main_ref = {"$ref": f"#/components/schemas/{struct_type.__name__}"}

    # Adiciona o modelo principal à lista de componentes
    components = {"schemas": {}}

    for model_name, model_schema in defs.items():
        fix_refs(model_schema)
        components["schemas"][model_name] = model_schema

    return main_ref, components


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
        """Decorator para registrar rotas e gerar documentação OpenAPI."""
        if settings.enable_swagger:
            request_content = None
            response_content = None
            response_422_content = None

            schema_error = convert_msgspec_schema_to_openapi(ErrorResponse)
            schema_error_generic = convert_msgspec_schema_to_openapi(
                ErrorResponseGeneric
            )
            schemas = openapi_spec["components"]["schemas"]
            schemas.update(schema_error[1]["schemas"])
            schemas.update(schema_error_generic[1]["schemas"])

            response_422_content = {
                "application/json": {"schema": {"$ref": schema_error[0]["$ref"]}}
            }

            response_400_content = {
                "application/json": {
                    "schema": {"$ref": schema_error_generic[0]["$ref"]}
                }
            }

            response_500_content = {
                "application/json": {
                    "schema": {"$ref": schema_error_generic[0]["$ref"]}
                }
            }

            if response_model:
                schema_response = convert_msgspec_schema_to_openapi(response_model)
                schemas.update(schema_response[1]["schemas"])

                response_content = {
                    "application/json": {"schema": {"$ref": schema_response[0]["$ref"]}}
                }

            if request_model:
                request_schema = convert_msgspec_schema_to_openapi(request_model)
                schemas.update(request_schema[1]["schemas"])

                request_content = {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {"$ref": request_schema[0]["$ref"]}
                        }
                    },
                }

            parameters = []

            if headers:
                for header in headers:
                    h = encode_dict(header)
                    parameters.append(h)

            if query_params:
                for q_param in query_params:
                    q = encode_dict(q_param)
                    parameters.append(q)

            if path_params:
                for p_param in path_params:
                    p = encode_dict(p_param)
                    parameters.append(p)

            if cookie_params:
                for c_param in cookie_params:
                    c = encode_dict(c_param)
                    parameters.append(c)

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
                        "content": response_422_content,
                    },
                    "400": {
                        "description": "Client Error",
                        "content": response_400_content,
                    },
                    "404": {
                        "description": "NotFound",
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "title": "ErrorNotFound",
                                    "type": "object",
                                    "properties": {
                                        "error": {"type": "string"}
                                    },
                                    "required": ["error"],
                                },
                            }
                        },
                    },
                    "500": {
                        "description": "Server Error",
                        "content": response_500_content,
                    },
                },
            }

        regex_pattern = compile_path_to_regex(path)
        routes_by_method[method.upper()].append((regex_pattern, path, func))

        routes[(path, method.upper())] = func

        # Armazena os metadados da rota na função decorada
        setattr(
            func,
            "__route_info__",
            {
                "request_model": request_model,
                "response_model": response_model,
                "query_params": query_params,
                "path_params": path_params,
                "cookie_params": cookie_params,
            },
        )

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


def get_route_details(method, path):
    if routes.get((path, method)):
        return (path, method.upper())

    return next(
        (
            (path_template, method.upper())
            for regex, path_template, _ in routes_by_method[
                method.upper()
            ]
            if regex.match(path)
        ),
        (path, method.upper()),
    )