import time

from prometheus_client import (
    # Counter,
    # Gauge,
    Histogram,
    CollectorRegistry,
    generate_latest,
    multiprocess,
)

from app.config import get_settings
from app.core.exception import AppException
from app.core.utils import send_response, text_plain_response
from app.core.routing import get, get_route_details

settings = get_settings()

HTTP_REQUEST_DURATION_SECONDS = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "path", "status_code"],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0, 7.5, 10.0),
)

IGNORED_PATHS = {"/metrics", "/docs", "/openapi.json", "/favicon.ico"}

def _prometheus_metrics():
    """Generate Prometheus metrics for the application."""
    if not settings.prometheus_multiproc_dir:
        return generate_latest()
    
    registry = CollectorRegistry()
    multiprocess.MultiProcessCollector(registry=registry)
    return generate_latest(registry)

if settings.enable_metrics:
    @get("/metrics", summary="METRICS", tags=["METRICS"], response_model=None)
    async def metrics(scope, receive, send):
        body = _prometheus_metrics()
        return await send_response(send, text_plain_response(body))


class PrometheusMiddleware:
    """Middleware para medir latência de requests e expor métricas."""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http" or scope["path"] in IGNORED_PATHS:
            return await self.app(scope, receive, send)

        start_time = time.perf_counter_ns()
        path, method = get_route_details(method=scope["method"], path=scope["path"])

        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                status_code = str(message["status"])
                HTTP_REQUEST_DURATION_SECONDS.labels(
                    method=method, path=path, status_code=status_code
                ).observe((time.perf_counter_ns() - start_time) / 1_000_000_000)
            await send(message)

        try:
            await self.app(scope, receive, send_wrapper)
        except Exception as e:
            status_code = str(e.status_code) if isinstance(e, AppException) else "500"
            HTTP_REQUEST_DURATION_SECONDS.labels(
                method=method, path=path, status_code=status_code
            ).observe((time.perf_counter_ns() - start_time) / 1_000_000_000)
            raise