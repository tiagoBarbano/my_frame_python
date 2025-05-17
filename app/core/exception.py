import http
import msgspec

from typing import Any, Mapping
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode
from app.config import get_settings
from app.core.logger import log
from app.dto.base_dto import BaseDto

settings = get_settings()
tracer = trace.get_tracer("error.tracer")


class ErrorResponseGeneric(BaseDto, kw_only=True):
    message: str
    error_detail: str


class ErrorDetail(msgspec.Struct):
    field: str
    message: str
    validator: str


class ErrorContent(msgspec.Struct):
    detail: list[ErrorDetail]
    body: Any


class ErrorResponse(msgspec.Struct):
    error: ErrorContent


class AppException(Exception):
    def __init__(
        self,
        detail: Any | None = None,
        headers: Mapping[str, str] | None = None,
        status_code: int = 400,
    ) -> None:
        if detail is None:
            detail = http.HTTPStatus(status_code).phrase
        self.detail = detail
        self.status_code = status_code
        self.headers = headers

        if settings.enable_tracing:
            with tracer.start_span(
                f"error.{status_code}", attributes={"force_sample": True}
            ) as span:
                span.set_status(Status(StatusCode.ERROR, detail))
                span.record_exception(self)

        log.error(self.detail, extra={"status_code": status_code})
        super().__init__(detail)

    def __str__(self) -> str:
        return f"{self.status_code}: {self.detail}"

    def __repr__(self) -> str:
        class_name = self.__class__.__name__
        return f"{class_name}(status_code={self.status_code!r}, detail={self.detail!r})"
