import msgspec

import tracing as otel

from app import app, json_response, read_body, send_response
from config import Settings
from router import post, get

from opentelemetry.instrumentation.asgi import OpenTelemetryMiddleware
from middleware import LoggerMiddleware
from prometheus import PrometheusMiddleware
from logger_conf import logger

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
    # logger.info("HelloWorld")
    return await send_response(send, json_response({"message": "HelloWorld"}))


# app = PrometheusMiddleware(app)
# app = OpenTelemetryMiddleware(app)