import msgspec

import tracing as otel  # noqa: F401
from metrics import PrometheusMiddleware, prometheus_metrics
from logger import LoggerMiddleware

from app import app, json_response, read_body, send_response, text_response
from routing import post, get

from opentelemetry.instrumentation.asgi import OpenTelemetryMiddleware
from opentelemetry.util.http import parse_excluded_urls

app = LoggerMiddleware(app)
app = PrometheusMiddleware(app)
app = OpenTelemetryMiddleware(app, excluded_urls=parse_excluded_urls("/metrics"), exclude_spans=["send", "receive"])


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


# Metricas do Prometheus
@get("/metrics")
async def metrics(scope, receive, send):
    body = prometheus_metrics()
    return await send_response(send, text_response(body))