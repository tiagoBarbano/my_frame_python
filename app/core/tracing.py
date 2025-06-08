from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider, sampling
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter  # noqa: F401
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter  # noqa: F401
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter as OTLPSpanExporterHTTP  # noqa: F401

from app.config import get_settings


settings = get_settings()


class ErrorAwareSampler(sampling.Sampler):
    """Sampler that respects the force_sample attribute in attributes."""

    def __init__(self, ratio: str):
        self.normal_sampler = sampling.TraceIdRatioBased(ratio)

    def should_sample(self, parent_context, trace_id, name, kind, attributes, links):
        if attributes and attributes.get("force_sample") is True:
            return sampling.SamplingResult(sampling.Decision.RECORD_AND_SAMPLE)
        return self.normal_sampler.should_sample(
            parent_context, trace_id, name, kind, attributes, links
        )

    def get_description(self):
        return f"ErrorAwareSampler({self.normal_sampler.get_description()})"


"""Responsável por habilitar o OpenTelemetry para o Tracing"""

exporter = (
    ConsoleSpanExporter()
    if settings.flag_local
    else OTLPSpanExporter(endpoint=settings.endpoint_otel, insecure=True)
)
    
# exporter = OTLPSpanExporterHTTP(endpoint=settings.endpoint_otel)


resource = Resource.create(attributes={"service.name": settings.app_name})
tracer = TracerProvider(
    resource=resource,
    sampler=ErrorAwareSampler(ratio=settings.ratio_value)
    if settings.enable_trace_ratio_based
    else None,
)

tracer.add_span_processor(
    BatchSpanProcessor(
        exporter,
        # max_export_batch_size=512,
        # schedule_delay_millis=1000,
        # max_queue_size=2048,
    )
)
trace.set_tracer_provider(tracer)

LoggingInstrumentor().instrument(tracer_provider=tracer)
