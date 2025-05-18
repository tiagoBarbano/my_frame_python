import pytest
import http

from app.core.exception import AppException

@pytest.mark.parametrize(
    "detail, headers, status_code, expected_detail, expected_status, expected_headers, test_id",
    [
        # Happy path: all fields provided
        ("Something went wrong", {"X-Test": "1"}, 422, "Something went wrong", 422, {"X-Test": "1"}, "all_fields_provided"),
        # Edge: detail is None, status_code is 404
        (None, None, 404, http.HTTPStatus(404).phrase, 404, None, "detail_none_status_404"),
        # Edge: headers is None, status_code is 500
        ("Internal error", None, 500, "Internal error", 500, None, "headers_none_status_500"),
        # Edge: detail is None, status_code is 400 (default)
        (None, None, 400, http.HTTPStatus(400).phrase, 400, None, "detail_none_status_default_400"),
        # Edge: custom headers, default detail
        (None, {"X-Edge": "yes"}, 401, http.HTTPStatus(401).phrase, 401, {"X-Edge": "yes"}, "custom_headers_default_detail"),
    ],
    ids=lambda x: x if isinstance(x, str) else None,
)
def test_appexception_init(monkeypatch, detail, headers, status_code, expected_detail, expected_status, expected_headers, test_id):
    # Arrange
    log_calls = []
    monkeypatch.setattr("app.core.exception.log", type("Log", (), {"error": staticmethod(lambda msg, extra=None: log_calls.append((msg, extra)))} )())
    monkeypatch.setattr("app.core.exception.settings", type("Settings", (), {"enable_tracing": False})())
    monkeypatch.setattr("app.core.exception.tracer", type("Tracer", (), {"start_span": lambda *a, **kw: DummySpan()})())

    # Act
    exc = AppException(detail=detail, headers=headers, status_code=status_code)

    # Assert
    assert exc.detail == expected_detail
    assert exc.status_code == expected_status
    assert exc.headers == expected_headers
    assert log_calls == [(expected_detail, {"status_code": expected_status})]
    assert isinstance(exc, Exception)

class DummySpan:
    def __enter__(self): return self
    def __exit__(self, exc_type, exc_val, exc_tb): pass
    def set_status(self, status): self.status = status
    def record_exception(self, exc): self.exc = exc

def test_appexception_tracing(monkeypatch):
    # Arrange
    log_calls = []
    span_calls = {}
    class DummySpanCtx:
        def __enter__(self): return self
        def __exit__(self, exc_type, exc_val, exc_tb): pass
        def set_status(self, status): span_calls["set_status"] = status
        def record_exception(self, exc): span_calls["record_exception"] = exc

    monkeypatch.setattr("app.core.exception.log", type("Log", (), {"error": staticmethod(lambda msg, extra=None: log_calls.append((msg, extra)))} )())
    monkeypatch.setattr("app.core.exception.settings", type("Settings", (), {"enable_tracing": True})())
    monkeypatch.setattr("app.core.exception.tracer", type("Tracer", (), {"start_span": lambda *a, **kw: DummySpanCtx()})())

    # Act
    exc = AppException(detail="trace error", status_code=418)

    # Assert
    assert exc.detail == "trace error"
    assert exc.status_code == 418
    assert "set_status" in span_calls
    assert "record_exception" in span_calls
    assert span_calls["record_exception"] is exc
    assert log_calls == [("trace error", {"status_code": 418})]

@pytest.mark.parametrize(
    "status_code, detail, expected_str, expected_repr, test_id",
    [
        (400, "Bad request", "400: Bad request", "AppException(status_code=400, detail='Bad request')", "str_repr_normal"),
        (404, "Not found", "404: Not found", "AppException(status_code=404, detail='Not found')", "str_repr_404"),
        (500, "Server error", "500: Server error", "AppException(status_code=500, detail='Server error')", "str_repr_500"),
    ],
    ids=lambda x: x if isinstance(x, str) else None,
)
def test_appexception_str_and_repr(monkeypatch, status_code, detail, expected_str, expected_repr, test_id):
    # Arrange
    monkeypatch.setattr("app.core.exception.log", type("Log", (), {"error": staticmethod(lambda msg, extra=None: None)})())
    monkeypatch.setattr("app.core.exception.settings", type("Settings", (), {"enable_tracing": False})())
    monkeypatch.setattr("app.core.exception.tracer", type("Tracer", (), {"start_span": lambda *a, **kw: DummySpan()})())

    # Act
    exc = AppException(detail=detail, status_code=status_code)

    # Assert
    assert str(exc) == expected_str
    assert repr(exc) == expected_repr

def test_appexception_inheritance(monkeypatch):
    # Arrange
    monkeypatch.setattr("app.core.exception.log", type("Log", (), {"error": staticmethod(lambda msg, extra=None: None)})())
    monkeypatch.setattr("app.core.exception.settings", type("Settings", (), {"enable_tracing": False})())
    monkeypatch.setattr("app.core.exception.tracer", type("Tracer", (), {"start_span": lambda *a, **kw: DummySpan()})())

    # Act
    exc = AppException("test")

    # Assert
    assert isinstance(exc, Exception)
    assert isinstance(exc, AppException)
