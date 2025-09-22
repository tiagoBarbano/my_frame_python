from functools import lru_cache
import msgspec

from collections import defaultdict
from typing import Optional, Tuple, Type, Union
from app.config import Settings
from app.core.exception import ErrorResponse, ErrorResponseGeneric
from app.core.utils import compile_path_to_regex
from app.core.params import HeaderParams, PathParams, QueryParams, CookieParams

settings = Settings()
routes = {}
routes_by_method = defaultdict(list)
RequestResponseType = Union[Type[msgspec.Struct], dict, None]


openapi_spec = {
    "openapi": "3.0.0",
    "info": {
        "title": settings.app_name,
        "version": "1.0.0",
        "summary": "A pet store manager.",
        "description": "This is an example server for a pet store.",
        "termsOfService": "https://example.com/terms/",
        "contact": {
            "name": "API Support",
            "url": "https://www.example.com/support",
            "email": "support@example.com",
        },
        "license": {
            "name": "Apache 2.0",
            "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
        },
    },
    "servers": [
        {
            "url": f"http://localhost:{settings.port_app}",
            "description": "Local server"
        },
        {
            "url": "https://api.example.com/v1",
            "description": "Production server (uses live data)"
        },
        {
            "url": "https://sandbox-api.example.com:8443/v1",
            "description": "Sandbox server (uses test data)"
        }
    ],    
    "paths": {},
    "components": {"schemas": {}},
}


def encode_dict(model) -> dict:
    """Gera dict para parâmetros OpenAPI a partir de HeaderParams, QueryParams, etc."""
    schema = {
        k: getattr(model, k)
        for k in (
            "type_field",
            "description",
            "enum",
            "pattern",
            "example",
            "maxLength",
            "minLength",
            "default",
        )
        if getattr(model, k, None) is not None
    }

    return {
        "name": model.name,
        "in": model._in,
        "required": model.required,
        "schema": schema,
        "deprecated": model.deprecated,
        "allowEmptyValue": model.allow_empty_value,
    }


@lru_cache(maxsize=128)
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

    # Adiciona o modelo principal à lista de componentes
    components = {"schemas": {}}

    for model_name, model_schema in defs.items():
        fix_refs(model_schema)
        components["schemas"][model_name] = model_schema

    # Modelo principal como referência
    main_ref = {"$ref": f"#/components/schemas/{struct_type.__name__}"}
    return main_ref, components


# ---- Decorator principal ----
def route(
    method: str,
    path: str,
    *,
    summary: str = "",
    description: Optional[str] = None,
    request_model: Optional[RequestResponseType] = None,
    response_model: Optional[RequestResponseType] = None,
    headers: Optional[list[HeaderParams]] = None,
    tags: Optional[list[str]] = None,
    query_params: Optional[list[QueryParams]] = None,
    path_params: Optional[list[PathParams]] = None,
    cookie_params: Optional[list[CookieParams]] = None,
    ms=None,
):
    """Registra rota e pré-processa schemas OpenAPI."""

    # Pré-compila regex
    regex_pattern = compile_path_to_regex(path)

    # Pré-processa schemas para OpenAPI (apenas se Swagger ativo)
    if settings.enable_swagger:
        schemas = openapi_spec["components"]["schemas"]

        # Erros padrão
        for error_model in [ErrorResponse, ErrorResponseGeneric]:
            ref, comp = convert_msgspec_schema_to_openapi(error_model)
            schemas.update(comp["schemas"])

        # Request e response
        request_content, response_content = None, None
        if request_model:
            ref, comp = convert_msgspec_schema_to_openapi(request_model)
            schemas.update(comp["schemas"])
            request_content = {
                "required": True,
                "content": {"application/json": {"schema": ref}},
            }

        if response_model:
            ref, comp = convert_msgspec_schema_to_openapi(response_model)
            schemas.update(comp["schemas"])
            response_content = {"application/json": {"schema": ref}}

        # Parâmetros OpenAPI
        parameters = []
        for param_list in [headers, query_params, path_params, cookie_params]:
            if param_list:
                parameters.extend(encode_dict(p) for p in param_list)

        # Atualiza openapi_spec
        openapi_spec["paths"].setdefault(path, {})[method] = {
            "summary": summary,
            "description": description,
            "tags": tags,
            "parameters": parameters,
            "requestBody": request_content,
            "responses": {
                "200": {"description": "Sucesso", "content": response_content},
                "422": {
                    "description": "Validation Error",
                    "content": {
                        "application/json": {
                            "$ref": "#/components/schemas/ErrorResponse"
                        }
                    },
                },
                "400": {
                    "description": "Client Error",
                    "content": {
                        "application/json": {
                            "$ref": "#/components/schemas/ErrorResponseGeneric"
                        }
                    },
                },
                "404": {
                    "description": "NotFound",
                    "required": True,
                    "content": {
                        "application/json": {
                            "type": "object",
                            "properties": {"error": {"type": "string"}},
                            "required": ["error"],
                        }
                    },
                },
                "500": {
                    "description": "Server Error",
                    "content": {
                        "application/json": {
                            "$ref": "#/components/schemas/ErrorResponseGeneric"
                        }
                    },
                },
            },
        }

    # Registro de rota
    routes_by_method[method.upper()].append((regex_pattern, path, func := None))
    routes[(path, method.upper())] = func

    def decorator(func):
        # Atualiza referência na rota
        routes[(path, method.upper())] = func
        routes_by_method[method.upper()][-1] = (regex_pattern, path, func)

        # Metadados
        setattr(
            func,
            "__route_info__",
            {
                "request_model": request_model,
                "response_model": response_model,
                "headers": headers,
                "query_params": query_params,
                "path_params": path_params,
                "cookie_params": cookie_params,
            },
        )
        return func

    return decorator


# --- Atalhos claros e legíveis ---
def get(
    path: str,
    *,
    summary: str = "",
    description: Optional[str] = None,
    request_model: Optional[RequestResponseType] = None,
    response_model: Optional[RequestResponseType] = None,
    headers: Optional[list[HeaderParams]] = None,
    tags: Optional[list[str]] = None,
    query_params: Optional[list[QueryParams]] = None,
    path_params: Optional[list[PathParams]] = None,
    cookie_params: Optional[list[CookieParams]] = None,
):
    return route(
        method="get",
        path=path,
        summary=summary,
        description=description,
        request_model=request_model,
        response_model=response_model,
        headers=headers,
        tags=tags,
        query_params=query_params,
        path_params=path_params,
        cookie_params=cookie_params,
    )


def post(
    path: str,
    *,
    summary: str = "",
    description: Optional[str] = None,
    request_model: Optional[RequestResponseType] = None,
    response_model: Optional[RequestResponseType] = None,
    headers: Optional[list[HeaderParams]] = None,
    tags: Optional[list[str]] = None,
    query_params: Optional[list[QueryParams]] = None,
    path_params: Optional[list[PathParams]] = None,
    cookie_params: Optional[list[CookieParams]] = None,
):
    return route(
        method="post",
        path=path,
        summary=summary,
        description=description,
        request_model=request_model,
        response_model=response_model,
        headers=headers,
        tags=tags,
        query_params=query_params,
        path_params=path_params,
        cookie_params=cookie_params,
    )


def get_route_details(method, path):
    if routes.get((path, method)):
        return (path, method.upper())

    return next(
        (
            (path_template, method.upper())
            for regex, path_template, _ in routes_by_method[method.upper()]
            if regex.match(path)
        ),
        (path, method.upper()),
    )
