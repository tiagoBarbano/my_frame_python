import msgspec

import _opentelemetry as otel

# from opentelemetry.instrumentation.asgi import OpenTelemetryMiddleware
# from middleware import LoggerMiddleware
# from prometheus import PrometheusMiddleware

from app import app, json_response, read_body, send_response
from config import Settings
from router import post, get

# app = PrometheusMiddleware(app)
# app = LoggerMiddleware(app)
# app = OpenTelemetryMiddleware(app)


set = Settings()


class User(msgspec.Struct):
    empresa: str
    valor: int


decode = msgspec.json.Decoder(type=User).decode
encode = msgspec.json.Encoder().encode


@post("/cotador")
async def cotador(scope, receive, send):
    body = await read_body(receive)
    data = decode(body)
    result = {"cotacao_final": data.valor * 1.23, "empresa": data.empresa}
    return await send_response(send, json_response(result))


@get("/")
async def hello_world(scope, receive, send):
    return await send_response(send, json_response({"message": "HelloWorld"}))
