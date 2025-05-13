import msgspec
from app.config import Settings

settings = Settings()
routes = {}

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
    headers: list = None,
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
                            "name": header["name"],
                            "in": "header",
                            "required": header.get("required", True),
                            "schema": {"type": header.get("type", "string")},
                            "description": header.get("description", ""),
                        }
                    )
                    
            openapi_spec["paths"].setdefault(path, {})[method] = {
                "summary": summary,
                "description": description,
                "parameters": parameters,
                "requestBody": request_content,
                "responses": {
                    "200": {
                        "description": "Sucesso",
                        "content": response_content,
                    }
                },
            }

        routes[(path, method.upper())] = func
        return func

    return decorator


# Atalhos para GET e POST
get = (
    lambda path,
    summary,
    description=None,
    request_model=None,
    response_model=None,
    headers=None: route(
        "get", path, summary, description, request_model, response_model, headers
    )
)
post = (
    lambda path,
    summary,
    description=None,
    request_model=None,
    response_model=None,
    headers=None: route(
        "post", path, summary, description, request_model, response_model, headers
    )
)
