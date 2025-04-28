import msgspec

import app.tracing as otel  # noqa: F401
from app.metrics import PrometheusMiddleware, prometheus_metrics
from app.logger import LoggerMiddleware

from app.app import app, json_response, read_body, send_response, text_response
from app.routing import post, get

from opentelemetry.instrumentation.asgi import OpenTelemetryMiddleware
from opentelemetry.util.http import parse_excluded_urls
from app.config import Settings

settings = Settings()

if settings.enable_logger:
    app = LoggerMiddleware(app)

# Metricas do Prometheus
if settings.enable_metrics:
    app = PrometheusMiddleware(app)
        
    @get("/metrics")
    async def metrics(scope, receive, send):
        body = prometheus_metrics()
        return await send_response(send, text_response(body))


if settings.enable_tracing:
    app = OpenTelemetryMiddleware(
        app,
        excluded_urls=parse_excluded_urls("/metrics"),
        exclude_spans=["send", "receive"],
    )


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


