import pytest
import types
from unittest.mock import AsyncMock, patch, MagicMock

from app.core.application import app
from app.core.exception import AppException


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "scope, handler_return, expected_send_calls, expected_handler_called, test_id",
    [
        # Lifespan scope
        (
            {"type": "lifespan", "method": "GET", "path": "/"},
            None,
            [],
            False,
            "lifespan_scope",
        ),
        # Exact route match
        (
            {"type": "http", "method": "GET", "path": "/exact"},
            "handler_result",
            [],
            True,
            "exact_route_match",
        ),
        # Regex route match
        (
            {"type": "http", "method": "GET", "path": "/user/123"},
            "regex_handler_result",
            [],
            True,
            "regex_route_match",
        ),
        # OpenAPI JSON
        (
            {"type": "http", "method": "GET", "path": "/openapi.json"},
            None,
            [{"type": "http.response.start"}, {"type": "http.response.body"}],
            False,
            "openapi_json",
        ),
        # Swagger UI
        (
            {"type": "http", "method": "GET", "path": "/docs"},
            None,
            [{"type": "http.response.start"}, {"type": "http.response.body"}],
            False,
            "swagger_ui",
        ),
        # 404 Not Found
        (
            {"type": "http", "method": "GET", "path": "/notfound"},
            None,
            [{"type": "http.response.start"}, {"type": "http.response.body"}],
            False,
            "not_found",
        ),
    ],
    ids=lambda x: x if isinstance(x, str) else None,
)
async def test_app_various_paths(
    scope, handler_return, expected_send_calls, expected_handler_called, test_id
):
    # Arrange
    send_calls = []

    async def send(message):
        send_calls.append(message)

    # Patch dependencies
    with (
        patch("app.core.application.lifespan", new=AsyncMock()) as mock_lifespan,
        patch(
            "app.core.application.routes",
            new={("/exact", "GET"): AsyncMock(return_value="handler_result")},
        ),
        patch(
            "app.core.application.routes_by_method",
            new={
                "GET": [
                    (
                        MagicMock(
                            match=MagicMock(
                                side_effect=lambda p: types.SimpleNamespace(
                                    groupdict=lambda: {"id": "123"}
                                )
                                if p == "/user/123"
                                else None
                            )
                        ),
                        "/user/{id}",
                        AsyncMock(return_value="regex_handler_result"),
                    )
                ]
            },
        ),
        patch("app.core.application.openapi_spec", new={"openapi": "spec"}),
        patch("app.core.application.send_response", new=AsyncMock()),
        patch(
            "app.core.application.json_response",
            new=MagicMock(return_value={"json": True}),
        ),
        patch(
            "app.core.application.text_html_response",
            new=MagicMock(return_value="html"),
        ),
        patch(
            "app.core.application.serve_swagger_ui",
            new=AsyncMock(return_value="swagger_html"),
        ),
    ):
        # Act
        result = await app(scope, None, send)

        # Assert
        if scope["type"] == "lifespan":
            assert mock_lifespan.await_count == 1
        elif scope["path"] == "/exact":
            assert result == "handler_result"
        elif scope["path"] == "/user/123":
            assert result == "regex_handler_result"
            assert scope.get("path_params") == {"id": "123"}
        elif scope["path"] == "/openapi.json":
            app.core.application.send_response.assert_awaited()
            app.core.application.json_response.assert_called_with({"openapi": "spec"})
        elif scope["path"] == "/docs":
            app.core.application.send_response.assert_awaited()
            app.core.application.text_html_response.assert_called_with(
                "swagger_html", status=200
            )
        elif scope["path"] == "/notfound":
            app.core.application.send_response.assert_awaited()
            app.core.application.json_response.assert_called_with(
                {"error": "Not found"}, 404
            )


@pytest.mark.asyncio
async def test_app_raises_appexception():
    # Arrange
    async def send(message):
        pass

    class DummyException(AppException):
        def __init__(self):
            super().__init__(
                detail={"msg": "fail"}, status_code=418, headers={"X-Test": "1"}
            )

    with (
        patch(
            "app.core.application.routes",
            new={("/fail", "GET"): AsyncMock(side_effect=DummyException)},
        ),
        patch("app.core.application.routes_by_method", new={"GET": []}),
        patch(
            "app.core.application.send_response", new=AsyncMock()
        ) as mock_send_response,
        patch(
            "app.core.application.json_response",
            new=MagicMock(return_value={"json": True}),
        ) as mock_json_response,
    ):
        scope = {"type": "http", "method": "GET", "path": "/fail"}

        # Act
        await app(scope, None, send)

        # Assert
        mock_json_response.assert_called_with(
            data={"msg": "fail"}, status=418, headers={"X-Test": "1"}
        )
        mock_send_response.assert_awaited()


@pytest.mark.asyncio
async def test_app_regex_route_sets_path_params():
    # Arrange
    async def send(message):
        pass

    async def handler(scope, receive, send):
        return scope["path_params"]

    regex = MagicMock()
    regex.match.return_value = types.SimpleNamespace(groupdict=lambda: {"foo": "bar"})

    with (
        patch("app.core.application.routes", new={}),
        patch(
            "app.core.application.routes_by_method",
            new={"GET": [(regex, "/foo/{foo}", handler)]},
        ),
        patch("app.core.application.send_response", new=AsyncMock()),
        patch("app.core.application.json_response", new=MagicMock()),
    ):
        scope = {"type": "http", "method": "GET", "path": "/foo/bar"}

        # Act
        result = await app(scope, None, send)

        # Assert
        assert result == {"foo": "bar"}


@pytest.mark.asyncio
async def test_app_handles_non_http_scope_type():
    # Arrange
    async def send(message):
        pass

    with (
        patch("app.core.application.lifespan", new=AsyncMock()) as mock_lifespan,
        patch("app.core.application.routes", new={}),
        patch("app.core.application.routes_by_method", new={}),
        patch("app.core.application.send_response", new=AsyncMock()),
        patch("app.core.application.json_response", new=MagicMock()),
    ):
        scope = {"type": "lifespan", "method": "GET", "path": "/"}

        # Act
        await app(scope, None, send)

        # Assert
        mock_lifespan.assert_awaited_once_with(scope, None, send)
