import logging
import sys
import orjson
import pytest
import types
from app.core.logger import OrjsonFormatter

# app/core/test_logger.py



def make_log_record(
    msg="test message",
    level=logging.INFO,
    name="test_logger",
    extra=None,
    exc_info=None,
):
    record = logging.LogRecord(
        name=name,
        level=level,
        pathname="dummy_path",
        lineno=42,
        msg=msg,
        args=(),
        exc_info=exc_info,
    )
    if extra:
        for k, v in extra.items():
            setattr(record, k, v)
    return record

def test_format_basic_fields():
    formatter = OrjsonFormatter()
    record = make_log_record()
    result = formatter.format(record)
    assert isinstance(result, bytes)
    data = orjson.loads(result)
    assert "time" in data
    assert data["level"] == "INFO"
    assert data["message"] == "test message"
    assert data["logger"] == "test_logger"
    assert result.endswith(b"\n")

def test_format_includes_extra_fields():
    formatter = OrjsonFormatter()
    record = make_log_record(extra={"user_id": 123, "custom": "abc"})
    result = formatter.format(record)
    data = orjson.loads(result)
    assert data["user_id"] == 123
    assert data["custom"] == "abc"

def test_format_with_exception_info():
    formatter = OrjsonFormatter()
    try:
        raise ValueError("fail!")
    except ValueError:
        exc_info = sys.exc_info()
        record = make_log_record(exc_info=exc_info)
        result = formatter.format(record)
        data = orjson.loads(result)
        assert "exception" in data
        assert "exception_type" in data
        assert data["exception_type"] == "ValueError"
        assert "fail!" in data["exception"]

def test_format_without_exception_info():
    formatter = OrjsonFormatter()
    record = make_log_record()
    result = formatter.format(record)
    data = orjson.loads(result)
    assert "exception" not in data
    assert "exception_type" not in data

def test_format_does_not_include_standard_keys():
    formatter = OrjsonFormatter()
    record = make_log_record()
    result = formatter.format(record)
    data = orjson.loads(result)
    # Should not include e.g. 'args', 'pathname', 'lineno'
    assert "args" not in data
    assert "pathname" not in data
    assert "lineno" not in data