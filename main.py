import os

from app.core.application import app
from app.config import Settings
from app.router import *  # noqa: F403


settings = Settings()

# Define a função principal do aplicativo
app = app

# Configuração dos Middlewares

# Habilita o Middleware de logger
if settings.enable_logger:
    from app.core.logger import LoggerMiddleware
    
    app = LoggerMiddleware(app)

# Habilita as Metricas do Prometheus
if settings.enable_metrics:
    from app.core.metrics import PrometheusMiddleware
    
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

