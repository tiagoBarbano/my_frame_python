import pytest
from types import SimpleNamespace

from app.core.routing import route


@pytest.mark.parametrize(
    "enable_swagger, request_model, response_model, headers, query_params, path_params, cookie_params, summary, tags, description, method, path, test_id",
    [
        # Happy path: all OpenAPI fields provided, swagger enabled
        (
            True,
            "RequestModel",
            "ResponseModel",
            [{"name": "X-Header", "in": "header"}],
            [{"name": "q", "in": "query"}],
            [{"name": "id", "in": "path"}],
            [{"name": "session", "in": "cookie"}],
            "Summary",
            ["tag1"],
            "Description",
            "get",
            "/items/{id}",
            "all_fields_swagger_enabled",
        ),
        # Edge: minimal OpenAPI, swagger enabled, no params/models
        (
            True,
            None,
            None,
            None,
            None,
            None,
            None,
            "Minimal",
            [],
            "",
            "post",
            "/minimal",
            "minimal_swagger_enabled",
        ),
        # Edge: swagger disabled, should skip OpenAPI logic
        (
            False,
            None,
            None,
            None,
            None,
            None,
            None,
            "NoSwagger",
            [],
            "",
            "put",
            "/noswagger",
            "swagger_disabled",
        ),
    ],
    ids=lambda x: x if isinstance(x, str) else None,
)
def test_route_various_cases(
    monkeypatch,
    enable_swagger,
    request_model,
    response_model,
    headers,
    query_params,
    path_params,
    cookie_params,
    summary,
    tags,
    description,
    method,
    path,
    test_id,
):
    # Arrange
    openapi_spec = {"components": {"schemas": {}}, "paths": {}}
    routes_by_method = {method.upper(): []}
    routes = {}

    # Patch settings
    monkeypatch.setattr(
        "app.core.routing.settings", SimpleNamespace(enable_swagger=enable_swagger)
    )
    # Patch openapi_spec, routes_by_method, routes
    monkeypatch.setattr("app.core.routing.openapi_spec", openapi_spec)
    monkeypatch.setattr("app.core.routing.routes_by_method", routes_by_method)
    monkeypatch.setattr("app.core.routing.routes", routes)
    # Patch convert_msgspec_schema_to_openapi to return dummy OpenAPI schema refs
    monkeypatch.setattr(
        "app.core.routing.convert_msgspec_schema_to_openapi",
        lambda model: (
            {"$ref": f"#/components/schemas/{model}"},
            {"schemas": {model: {"type": "object"}}},
        ),
    )
    # Patch compile_path_to_regex to return a dummy regex object
    monkeypatch.setattr(
        "app.core.routing.compile_path_to_regex", lambda p: f"regex({p})"
    )
    # Patch encode_dict to just return the dict
    monkeypatch.setattr("app.core.routing.encode_dict", lambda d: d)
    # Patch ErrorResponse and ErrorResponseGeneric to dummy names
    monkeypatch.setattr("app.core.routing.ErrorResponse", "ErrorResponse")
    monkeypatch.setattr("app.core.routing.ErrorResponseGeneric", "ErrorResponseGeneric")

    # Define a dummy function to decorate
    def dummy_func():
        return "ok"

    # Act
    decorator = route(
        method=method,
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
    decorated = decorator(dummy_func)

    # Assert
    assert decorated is dummy_func
    # Route should be registered in routes
    assert routes[(path, method.upper())] is dummy_func
    # Route should be registered in routes_by_method
    assert any(t[2] is dummy_func for t in routes_by_method[method.upper()])
    # __route_info__ should be set
    assert hasattr(dummy_func, "__route_info__")
    info = dummy_func.__route_info__
    assert info["request_model"] == request_model
    assert info["response_model"] == response_model
    assert info["query_params"] == query_params
    assert info["path_params"] == path_params
    assert info["cookie_params"] == cookie_params

    if enable_swagger:
        # OpenAPI path should be set
        assert path in openapi_spec["paths"]
        assert method in openapi_spec["paths"][path]
        op = openapi_spec["paths"][path][method]
        assert op["summary"] == summary
        assert op["tags"] == tags
        assert op["description"] == description
        # Should always have 400, 404, 422, 500 responses
        for code in ("400", "404", "422", "500"):
            assert code in op["responses"]
        # Should have parameters key
        assert "parameters" in op
        # Should have requestBody key (may be None)
        assert "requestBody" in op
    else:
        # OpenAPI spec should not be updated
        assert openapi_spec["paths"] == {}


def test_route_multiple_params(monkeypatch):
    # Arrange
    openapi_spec = {"components": {"schemas": {}}, "paths": {}}
    routes_by_method = {"POST": []}
    routes = {}
    monkeypatch.setattr(
        "app.core.routing.settings", SimpleNamespace(enable_swagger=True)
    )
    monkeypatch.setattr("app.core.routing.openapi_spec", openapi_spec)
    monkeypatch.setattr("app.core.routing.routes_by_method", routes_by_method)
    monkeypatch.setattr("app.core.routing.routes", routes)
    monkeypatch.setattr(
        "app.core.routing.convert_msgspec_schema_to_openapi",
        lambda model: (
            {"$ref": f"#/components/schemas/{model}"},
            {"schemas": {model: {"type": "object"}}},
        ),
    )
    monkeypatch.setattr(
        "app.core.routing.compile_path_to_regex", lambda p: f"regex({p})"
    )
    monkeypatch.setattr(
        "app.core.routing.encode_dict", lambda d: {"encoded": d["name"]}
    )
    monkeypatch.setattr("app.core.routing.ErrorResponse", "ErrorResponse")
    monkeypatch.setattr("app.core.routing.ErrorResponseGeneric", "ErrorResponseGeneric")

    headers = [{"name": "A", "in": "header"}, {"name": "B", "in": "header"}]
    query_params = [{"name": "q1", "in": "query"}]
    path_params = [{"name": "id", "in": "path"}]
    cookie_params = [{"name": "c", "in": "cookie"}]

    def dummy_func():
        return "ok"

    # Act
    decorator = route(
        method="POST",
        path="/multi",
        summary="Multi",
        description="desc",
        request_model=None,
        response_model=None,
        headers=headers,
        tags=["multi"],
        query_params=query_params,
        path_params=path_params,
        cookie_params=cookie_params,
    )
    decorated = decorator(dummy_func)

    # Assert
    assert decorated is dummy_func
    op = openapi_spec["paths"]["/multi"]["POST"]
    # All parameters should be encoded
    assert {"encoded": "A"} in op["parameters"]
    assert {"encoded": "B"} in op["parameters"]
    assert {"encoded": "q1"} in op["parameters"]
    assert {"encoded": "id"} in op["parameters"]
    assert {"encoded": "c"} in op["parameters"]
