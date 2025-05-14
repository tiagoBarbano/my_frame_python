import logging
import sys
import orjson
import time
import threading
import queue
import atexit

from functools import lru_cache

from app.config import get_settings


settings = get_settings()
_LOG_QUEUE = queue.Queue()
_SHUTDOWN = object()


class OrjsonFormatter(logging.Formatter):
    """
    Custom JSON formatter for logging.
    This formatter uses orjson to serialize log records into JSON format.
    It includes the timestamp, log level, message, and logger name.
    It also handles exceptions and any additional attributes in the log record.
    """
    __slots__ = ()

    def format(self, record):
        log_record = {
            "time": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(record.created)),
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
        }

        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)

        standard_keys = logging.LogRecord(
            "", "", "", "", "", "", "", ""
        ).__dict__.keys()
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
    """
    Setup logging for the application.
    This function configures the logging settings based on the application settings.
    It creates a logger with the specified log level and adds a custom handler to it.
    The logger is used to log messages in JSON format using the OrjsonFormatter.
    """
    
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

_writer_thread = threading.Thread(target=_log_writer, daemon=True).start()

atexit.register(_shutdown_logging)


class LoggerMiddleware:
    """Middleware to log request and response details."""
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
        
        start_time = time.perf_counter()        
        
        log.info("start_process", extra={"method": scope["method"], "path": scope["path"]})

        status_code = 200
        body_parts = []

        async def send_wrapper(message):
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = message["status"]
            elif message["type"] == "http.response.body":
                body_parts.append(message.get("body", b""))
            await send(message)

        await self.app(scope, receive, send_wrapper)

        finish_time = time.perf_counter()

        log.info(
            "finish_process",
            extra={
                "method": scope["method"],
                "path": scope["path"],
                "status_code": status_code,
                "time_process": finish_time - start_time,
            },
        )