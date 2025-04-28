from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter  # noqa: F401
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter  # noqa: F401

from config import Settings


settings = Settings()

"""Responsável por habilitar o OpenTelemetry para o Tracing"""
resource = Resource.create(attributes={"service.name": settings.app_name})
tracer = TracerProvider(resource=resource)

tracer.add_span_processor(
   BatchSpanProcessor(
      OTLPSpanExporter(
            endpoint="http://tempo:4317",
            insecure=True,
      )
   )
)
trace.set_tracer_provider(tracer)

LoggingInstrumentor().instrument(tracer_provider=tracer) 
