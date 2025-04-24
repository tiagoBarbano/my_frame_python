import orjson
from prometheus_client import Counter, generate_latest

from router import routes


from prometheus_client import make_asgi_app

# Métrica de exemplo
REQUEST_COUNT = Counter("http_requests_total", "Total HTTP requests")

metrics_app = make_asgi_app()


async def app(scope, receive, send):
    assert scope["type"] == "http"
    method = scope["method"]
    path = scope["path"]

    handler = routes.get((path, method))
    if handler:
        return await handler(scope, receive, send)

    # if scope["path"].startswith("/metrics"):
    #     await metrics_app(scope, receive, send)

    if path == "/metrics":
        body = generate_latest()
        await send({
            "type": "http.response.start",
            "status": 200,
            "headers": [(b"content-type", b"text/plain")],
        })
        await send({"type": "http.response.body", "body": body})
        return

    # Default 404
    return await send_response(send, json_response({"error": "Not found"}, 404))


# Helpers
def json_response(data, status=200):
    return status, [(b"content-type", b"application/json")], [orjson.dumps(data)]


# Leitura do corpo da requisição
async def read_body(receive):
    body = b""
    while True:
        message = await receive()
        if message["type"] == "http.request":
            body += message.get("body", b"")
            if not message.get("more_body", False):
                break
    return body


# Envio da resposta
async def send_response(send, response):
    status, headers, body = response
    await send({"type": "http.response.start", "status": status, "headers": headers})
    for chunk in body:
        await send({"type": "http.response.body", "body": chunk})
