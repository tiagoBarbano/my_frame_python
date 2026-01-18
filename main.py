import multiprocessing
import os

from app.routers.router import *  # noqa: F403

from granian import Granian
from app.config import Settings
from app.core.application import app

settings = Settings()


if settings.enable_logger:
    from app.core.logger import LoggerMiddleware

    app = LoggerMiddleware(app)


if __name__ == "__main__":
    workers = multiprocessing.cpu_count()

    Granian(
        "main:app",
        address="0.0.0.0",
        port=settings.port_app,
        interface="asgi",
        workers=settings.worker or workers,
        runtime_mode=settings.granian_runtime_mode,
        backlog=16384,
        backpressure=4096,
        websockets=False,
        log_enabled=False,
    ).serve()


# Habilita as Metricas do Prometheus
# if settings.enable_metrics:  
#     if settings.prometheus_multiproc_dir:
#         os.environ["PROMETHEUS_MULTIPROC_DIR"] = os.path.abspath("./metrics")
#         os.makedirs(os.environ["PROMETHEUS_MULTIPROC_DIR"], exist_ok=True)

#     from app.core.metrics import PrometheusMiddleware        

#     app = PrometheusMiddleware(app)

# Habilita o Tracing do OpenTelemetry
# if settings.enable_tracing:
#     import app.core.tracing as otel  # noqa: F401
#     from opentelemetry.instrumentation.asgi import OpenTelemetryMiddleware
#     from opentelemetry.util.http import parse_excluded_urls
#     from opentelemetry.semconv.attributes.http_attributes import HTTP_ROUTE
#     from app.core.routing import get_route_details

#     def _get_default_span_details(scope):
#         route, method = get_route_details(method=scope["method"], path=scope["path"])
#         attributes = {HTTP_ROUTE: route}
#         span_name = f"{method} {route}"

#         return span_name, attributes

#     app = OpenTelemetryMiddleware(
#         app,
#         excluded_urls=parse_excluded_urls("/metrics,/openapi.json,/docs"),
#         exclude_spans=["send", "receive"],
#         default_span_details=_get_default_span_details,
#     )
