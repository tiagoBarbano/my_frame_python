import time

from prometheus_client import (
    Histogram,
    CollectorRegistry,
    generate_latest,
    multiprocess,
)

from app.config import get_settings
from app.core.application import send_response, text_plain_response
from app.core.routing import get

settings = get_settings()


def prometheus_metrics():
    if settings.prometheus_multiproc_dir:
        registry = CollectorRegistry()
        multiprocess.MultiProcessCollector(registry)
        return generate_latest(registry)
    else:
        return generate_latest()


REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds", "Request latency", ["method", "path", "status"]
)

if settings.enable_metrics:

    @get("/metrics", summary="METRICS")
    async def hello_world(scope, receive, send):
        body = prometheus_metrics()
        return await send_response(send, text_plain_response(body))


class PrometheusMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        start_time = time.monotonic_ns()

        if (
            scope["type"] != "http"
            or scope["path"] == "/metrics"
            or scope["path"] == "/docs"
            or scope["path"] == "/openapi.json"
            or scope["path"] == "/favicon.ico"
        ):
            return await self.app(scope, receive, send)

        method = scope["method"]
        path = scope["path"]
        status_code = 500

        async def send_wrapper(message):
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = message["status"]
            await send(message)

        await self.app(scope, receive, send_wrapper)

        duration = (time.monotonic_ns() - start_time) / 1_000_000_000
        REQUEST_LATENCY.labels(method, path, str(status_code)).observe(duration)
