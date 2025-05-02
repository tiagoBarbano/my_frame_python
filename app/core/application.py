import orjson

from app.core.exception import AppException
from app.core.routing import routes, openapi_spec
from app.config import get_settings
from app.infra.database import MongoDB
from app.infra.redis import RedisClient

settings = get_settings()

def startup():
    RedisClient.init("redis://localhost:6379")
    MongoDB.init("mongodb://localhost:27017", db_name="mydb")
    

async def app(scope, receive, send):
    try:
        if scope["type"] == "lifespan":
            startup()
            
        method = scope["method"]
        path = scope["path"]

        handler = routes.get((path, method))
        if handler:
            return await handler(scope, receive, send)

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
