import multiprocessing
import os

from app.infra.lifespan import shutdown
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
        port=8000,
        workers=settings.worker if settings.worker else workers,
        backlog=16384,
        runtime_mode=settings.granian_runtime_mode,
        interface="asgi",
        http="1",
        websockets=False,
        # on_shutdown=shutdown
    ).serve()



# Habilita as Metricas do Prometheus
if settings.enable_metrics:
    from app.core.metrics import PrometheusMiddleware

    if settings.prometheus_multiproc_dir:
        os.makedirs(settings.prometheus_multiproc_dir, exist_ok=True)

    app = PrometheusMiddleware(app)

# Habilita o Tracing do OpenTelemetry
if settings.enable_tracing:
    import app.core.tracing as otel  # noqa: F401
    from opentelemetry.instrumentation.asgi import OpenTelemetryMiddleware
    from opentelemetry.util.http import parse_excluded_urls

    app = OpenTelemetryMiddleware(
        app,
        excluded_urls=parse_excluded_urls("/metrics,/openapi.json,/docs"),
        exclude_spans=["send", "receive"],
    )
