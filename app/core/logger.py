import logging
import sys
import orjson
import time
import threading
import queue
import atexit

from opentelemetry import trace
from functools import lru_cache

from app.config import Settings


settings = Settings()
_LOG_QUEUE = queue.Queue()
_SHUTDOWN = object()

class OrjsonFormatter(logging.Formatter):
    __slots__ = ()

    def format(self, record):
        log_record = {
            "time": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(record.created)),
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
        }

        span = trace.get_current_span()
        span_context = span.get_span_context()
        if span_context and span_context.is_valid:
            log_record["trace_id"] = format(span_context.trace_id, "032x")
            log_record["span_id"] = format(span_context.span_id, "016x")

        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)

        # Adiciona campos extras
        standard_keys = logging.LogRecord('', '', '', '', '', '', '', '').__dict__.keys()
        for key, value in record.__dict__.items():
            if key not in standard_keys and key not in log_record:
                log_record[key] = value            

        return orjson.dumps(log_record, option=orjson.OPT_APPEND_NEWLINE)

def _log_writer():
    stream = sys.stdout.buffer
    while True:
        record = _LOG_QUEUE.get()
        if record is _SHUTDOWN:
            break
        stream.write(record)
        stream.flush()

@lru_cache()
def _setup_logging() -> logging.Logger:
    log_level = settings.logger_level.upper()
    formatter = OrjsonFormatter()

    class QueueHandler(logging.Handler):
        def emit(self, record):
            try:
                msg = formatter.format(record)
                _LOG_QUEUE.put_nowait(msg)
            except Exception:
                pass

    handler = QueueHandler()

    root = logging.getLogger()
    root.setLevel(log_level)
    root.handlers.clear()
    root.addHandler(handler)

    return logging.getLogger(settings.app_name)

def _shutdown_logging():
    try:
        _LOG_QUEUE.put(_SHUTDOWN)
        _writer_thread.join()
    except Exception:
        pass

log = _setup_logging()

_writer_thread = threading.Thread(target=_log_writer, daemon=True)
_writer_thread.start()

atexit.register(_shutdown_logging)


class LoggerMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            log.info(f"{scope['method']} {scope['path']}")
        await self.app(scope, receive, send)
