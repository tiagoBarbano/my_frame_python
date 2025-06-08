import time

from prometheus_client import (
    Counter,
    Gauge,
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


def _prometheus_metrics():
    """Generate Prometheus metrics for the application."""
    if not settings.prometheus_multiproc_dir:
        return generate_latest()
    
    registry = CollectorRegistry()
    multiprocess.MultiProcessCollector(registry=registry)
    return generate_latest(registry)


# HTTP_REQUESTS_TOTAL = Counter(
#     "http_requests_total",
#     "Total number of HTTP requests",
#     ["method", "path", "status_code"],
# )

HTTP_REQUEST_DURATION_SECONDS = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "path", "status_code"],
    buckets=(
        0.005,
        0.01,
        0.025,
        0.05,
        0.075,
        0.1,
        0.25,
        0.5,
        0.75,
        1.0,
        2.5,
        5.0,
        7.5,
        10.0,
    ),
)

HTTP_REQUESTS_IN_PROGRESS = Gauge(
    "http_requests_in_progress",
    "Number of HTTP requests in progress",
    ["method", "path"],
)

# HTTP_RESPONSES_TOTAL = Counter(
#     "http_responses_total",
#     "Total number of HTTP responses",
#     ["method", "path", "status_code"],
# )

MAX_HTTP_REQUEST_DURATION_SECONDS = Gauge(
    "max_http_request_duration_seconds",
    "Maximum observed HTTP request duration in seconds",
    ["method", "path"]
)

if settings.enable_metrics:
    @get("/metrics", summary="METRICS", tags=["METRICS"], response_model=None)
    async def metrics(scope, receive, send):
        body = _prometheus_metrics()
        return await send_response(send, text_plain_response(body))


class PrometheusMiddleware:
    """Middleware to measure request latency and expose metrics."""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if (
            scope["type"] != "http"
            or scope["path"] == "/metrics"
            or scope["path"] == "/docs"
            or scope["path"] == "/openapi.json"
            or scope["path"] == "/favicon.ico"
        ):
            return await self.app(scope, receive, send)

        start_time = time.perf_counter_ns()
        path, method = get_route_details(method=scope["method"], path=scope["path"])
        
        labels = dict(
            method=method,
            path=path,
        )
        
        in_progress = HTTP_REQUESTS_IN_PROGRESS.labels(**labels)
        in_progress.inc()
        
        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                status_code = str(message["status"])
                labels_status = {**labels, "status_code": status_code}
                # req_total = HTTP_REQUESTS_TOTAL.labels(**labels_status)
                # resp_total = HTTP_RESPONSES_TOTAL.labels(**labels_status)
                duration_hist = HTTP_REQUEST_DURATION_SECONDS.labels(**labels_status)
                max_gauge = MAX_HTTP_REQUEST_DURATION_SECONDS.labels(**labels)

                # req_total.inc()
                # resp_total.inc()
                duration = (time.perf_counter_ns() - start_time) / 1_000_000_000
                duration_hist.observe(duration)
                prev_max = max_gauge._value.get()
                if duration > prev_max:
                    max_gauge.set(duration)
            await send(message)

        try:
            await self.app(scope, receive, send_wrapper)
        except Exception as e:
            status_code = "500"
            if isinstance(e, AppException):
                status_code = str(e.status_code)
            labels_status = {**labels, "status_code": status_code}
            # HTTP_REQUESTS_TOTAL.labels(**labels_status).inc()
            # HTTP_RESPONSES_TOTAL.labels(**labels_status).inc()
            duration = (time.perf_counter_ns() - start_time) / 1_000_000_000
            HTTP_REQUEST_DURATION_SECONDS.labels(**labels_status).observe(duration)
            raise
        finally:
            in_progress.dec()