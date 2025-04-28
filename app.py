import orjson

from routing import routes
from config import Settings

settings = Settings()


async def app(scope, receive, send):
    method = scope["method"]
    path = scope["path"]

    handler = routes.get((path, method))
    if handler:
        return await handler(scope, receive, send)

    return await send_response(send, json_response({"error": "Not found"}, 404))


def json_response(data, status=200):
    return status, [(b"content-type", b"application/json")], [orjson.dumps(data)]


def text_response(data, status=200):
    return status, [(b"content-type", b"text/plain")], [data]


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
