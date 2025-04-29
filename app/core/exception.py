from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode
from app.core.logger import log

tracer = trace.get_tracer("error.tracer")


class AppException(Exception):
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code

        with tracer.start_span(f"error.{status_code}", attributes={"force_sample": True}) as span:
            span.set_status(Status(StatusCode.ERROR, message))
            span.record_exception(self)

        log.error(self.message, extra={"status_code":status_code})
        super().__init__(message)
