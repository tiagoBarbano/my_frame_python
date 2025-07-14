from app.core.exception import AppException
from app.core.routing import openapi_spec, routes_by_method, routes
from app.config import get_settings
from app.core.swagger import serve_swagger_ui
from app.infra.lifespan import lifespan
from app.core.utils import send_response, json_response, text_html_response


settings = get_settings()

async def app(scope, receive, send):
    """
        ASGI application callable.
        This function handles incoming requests and routes them to the appropriate handler.
        It also manages the lifespan of the application and handles exceptions.
        The function takes the ASGI scope, receive channel, and send channel as input.
        It first checks if the scope type is "lifespan" and calls the lifespan function.
        Then, it retrieves the HTTP method and path from the scope.
        It checks for an exact route match, a regex route match, and handles OpenAPI JSON and Swagger UI requests.
        If no match is found, it returns a 404 Not Found response.
        If an AppException is raised, it returns the error message and status code.
    """
    
    try:
        if scope["type"] == "lifespan":
            await lifespan(scope, receive, send)

        method = scope["method"]
        path = scope["path"]

        if handler := routes.get((path, method)):
            return await handler(scope, receive, send)

        # 2. Rota com regex
        for regex, path_template, handler in routes_by_method[method.upper()]:
            if match := regex.match(path):
                scope["path_params"] = match.groupdict()
                return await handler(scope, receive, send)

        # 3. OpenAPI JSON
        if path == "/openapi.json":
            return await send_response(send, json_response(openapi_spec))

        # 4. Swagger UI
        if path == "/docs" and settings.enable_swagger:
            return await send_response(
                send, text_html_response(await serve_swagger_ui(), status=200)
            )

        # 5. 404 Not Found
        return await send_response(send, json_response({"error": "Not found"}, 404))
    except AppException as ex:
        body = ex.detail
        status_code = ex.status_code
        headers = ex.headers
        return await send_response(send, json_response(data=body, status=status_code, headers=headers))
