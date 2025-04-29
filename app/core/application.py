import orjson

from app.core.metrics import prometheus_metrics
from app.core.routing import routes, openapi_spec
from app.config import Settings

settings = Settings()


async def app(scope, receive, send):
    method = scope["method"]
    path = scope["path"]

    handler = routes.get((path, method))
    if handler:
        return await handler(scope, receive, send)

    if settings.enable_metrics:
        if path == "/metrics":
            body = prometheus_metrics()
            return await send_response(send, text_plain_response(body))

    if settings.enable_swagger:
        if path == "/openapi.json":
            return await send_response(send, json_response(openapi_spec))

        if path == "/docs":
            index_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Swagger UI</title>
                <link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist/swagger-ui.css" />
            </head>
            <body>
                <div id="swagger-ui"></div>
                <script src="https://unpkg.com/swagger-ui-dist/swagger-ui-bundle.js"></script>
                <script>
                const ui = SwaggerUIBundle({{
                    url: '/openapi.json',
                    dom_id: '#swagger-ui',
                    }});
                </script>
            </body>
            </html>
            """  # noqa: F541
            return await send_response(send, text_html_response(index_html.encode("utf-8")))

    return await send_response(send, json_response({"error": "Not found"}, 404))


def json_response(data, status=200):
    return status, [(b"content-type", b"application/json")], [orjson.dumps(data)]


def text_plain_response(data, status=200):
    return status, [(b"content-type", b"text/plain")], [data]


def text_html_response(data, status=200):
    return status, [(b"content-type", b"text/html")], [data]


async def read_body(receive):
    body = b""
    while True:
        message = await receive()
        if message["type"] == "http.request":
            body += message.get("body", b"")
            if not message.get("more_body", False):
                break
    return body


async def send_response(send, response):
    status, headers, body = response
    await send({"type": "http.response.start", "status": status, "headers": headers})
    for chunk in body:
        await send({"type": "http.response.body", "body": chunk})
