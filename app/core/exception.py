from typing import Mapping
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode
from app.core.logger import log

import http

tracer = trace.get_tracer("error.tracer")


class AppException(Exception):
    def __init__(self, detail: str | None = None,  headers: Mapping[str, str] | None = None, status_code: int = 400) -> None:
        if detail is None:
            detail = http.HTTPStatus(status_code).phrase
        self.detail = detail
        self.status_code = status_code
        self.headers = headers

        with tracer.start_span(f"error.{status_code}", attributes={"force_sample": True}) as span:
            span.set_status(Status(StatusCode.ERROR, detail))
            span.record_exception(self)

        log.error(self.detail, extra={"status_code":status_code})
        super().__init__(detail)

    def __str__(self) -> str:
        return f"{self.status_code}: {self.detail}"

    def __repr__(self) -> str:
        class_name = self.__class__.__name__
        return f"{class_name}(status_code={self.status_code!r}, detail={self.detail!r})"