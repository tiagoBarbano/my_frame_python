from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

from config import Settings


settings = Settings()

"""Responsável por habilitar o OpenTelemetry para o Tracing"""
resource = Resource.create(attributes={"service.name": settings.app_name})
tracer = TracerProvider(resource=resource)

# tracer.add_span_processor(
#    BatchSpanProcessor(
#       OTLPSpanExporter(
#             endpoint="http://localhost:4317",
#             # headers={"x-otlp-version": "0.7.0"},
#             insecure=True,
#       )
#    )
# )
trace.set_tracer_provider(tracer)

LoggingInstrumentor().instrument(tracer_provider=tracer) 