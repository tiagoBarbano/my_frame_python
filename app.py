import orjson
from prometheus_client import CollectorRegistry, generate_latest, multiprocess

def prometheus_metrics():
    registry = CollectorRegistry()
    multiprocess.MultiProcessCollector(registry)
    return generate_latest(registry)


from router import routes



async def app(scope, receive, send):
    assert scope["type"] == "http"
    method = scope["method"]
    path = scope["path"]

    handler = routes.get((path, method))
    if handler:
        return await handler(scope, receive, send)

    if path == "/metrics":
        body = prometheus_metrics()
        await send({
            "type": "http.response.start",
            "status": 200,
            "headers": [(b"content-type", b"text/plain")],
        })
        await send({"type": "http.response.body", "body": body})
        return

    return await send_response(send, json_response({"error": "Not found"}, 404))


def json_response(data, status=200):
    return status, [(b"content-type", b"application/json")], [orjson.dumps(data)]


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
