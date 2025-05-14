import orjson

from app.core.exception import AppException
from app.core.routing import openapi_spec, routes_by_method
from app.config import get_settings
from app.infra.database import MongoDB
from app.infra.redis import RedisClient


settings = get_settings()


def startup():
    RedisClient.init()
    MongoDB.init()


def shutdown():
    RedisClient.close()
    MongoDB.close()


async def lifespan(scope, receive, send):
    msg = await receive()
    if msg["type"] == "lifespan.startup":
        startup()
        await send({"type": "lifespan.startup.complete"})
    elif msg["type"] == "lifespan.shutdown":
        shutdown()
        print("Shutting down...")
        await send({"type": "lifespan.shutdown.complete"})


async def app(scope, receive, send):
    try:
        if scope["type"] == "lifespan":
            await lifespan(scope, receive, send)

        method = scope["method"]
        path = scope["path"]

        handler = {}

        for regex, path_template, handler in routes_by_method[method.upper()]:
            match = regex.match(path)
            if match:
                scope["path_params"] = match.groupdict()
                return await handler(scope, receive, send)

        if path == "/openapi.json":
            return await send_response(send, json_response(openapi_spec))

        if path == "/docs":
            index_html = f"""<!DOCTYPE html>
    <html>
    <head>
        <title>Swagger UI</title>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/5.11.0/swagger-ui.min.css" />
    </head>
    <body>
        <div id="swagger-ui"></div>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/5.11.0/swagger-ui-bundle.min.js"></script>
        <script>
        window.onload = () => {{
            SwaggerUIBundle({{
                url: '/openapi.json',
                dom_id: '#swagger-ui',
            }});
        }};
        </script>
    </body>
    </html>"""  # noqa: F541
            return await send_response(
                send, text_html_response(index_html.encode("utf-8"))
            )

        return await send_response(send, json_response({"error": "Not found"}, 404))
    except AppException as ex:
        body = ex.message
        status_code = ex.status_code
        return await send_response(send, json_response(body, status=status_code))


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
