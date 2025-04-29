import app.core.tracing as otel  # noqa: F401

from app.core.metrics import PrometheusMiddleware
from app.core.logger import LoggerMiddleware
from app.core.application import app
from app.config import Settings
from app.router import *


from opentelemetry.instrumentation.asgi import OpenTelemetryMiddleware
from opentelemetry.util.http import parse_excluded_urls

settings = Settings()

# Define a função principal do aplicativo
app = app

# Configuração dos Middlewares
# Habilita o Middleware de logger
if settings.enable_logger:
    app = LoggerMiddleware(app)

# Habilita as Metricas do Prometheus
if settings.enable_metrics:
    app = PrometheusMiddleware(app)

# Habilita o Tracing do OpenTelemetry
if settings.enable_tracing:
    app = OpenTelemetryMiddleware(
        app,
        excluded_urls=parse_excluded_urls("/metrics,/openapi.json,/docs"),	
        exclude_spans=["send", "receive"],
    )

