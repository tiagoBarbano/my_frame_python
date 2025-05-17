import contextlib
import logging
import sys
import orjson
import time

from functools import lru_cache

from app.config import get_settings

import asyncio


settings = get_settings()
_LOG_QUEUE = asyncio.Queue()
_SHUTDOWN = object()
_STANDARD_KEYS = frozenset(
    logging.LogRecord("", "", "", "", "", "", "", "").__dict__.keys()
)


class OrjsonFormatter(logging.Formatter):
    """
    Custom JSON formatter for logging.
    This formatter uses orjson to serialize log records into JSON format.
    It includes the timestamp, log level, message, and logger name.
    It also handles exceptions and any additional attributes in the log record.
    """

    __slots__ = ()

    def format(self, record):
        # Usa cache local de métodos
        record_dict = record.__dict__
        log_record = {
            "time": record.created,
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
        }

        # Evita chamada cara se não tiver exceção
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)
            log_record["exception_type"] = record.exc_info[0].__name__

        # Adiciona extras (campos customizados)
        for key in record_dict:
            if key not in _STANDARD_KEYS and key not in log_record:
                log_record[key] = record_dict[key]

        return orjson.dumps(log_record, option=orjson.OPT_APPEND_NEWLINE)


async def _log_writer():
    stream = sys.stdout.buffer
    write = stream.write
    flush = stream.flush

    BATCH_SIZE = 100
    FLUSH_INTERVAL = 0.05  # segundos

    buffer = []

    with contextlib.suppress(asyncio.CancelledError):
        while True:
            try:
                record = await asyncio.wait_for(
                    _LOG_QUEUE.get(), timeout=FLUSH_INTERVAL
                )
                if record is _SHUTDOWN:
                    break
                buffer.append(record)

                if len(buffer) >= BATCH_SIZE:
                    write(b"".join(buffer))
                    flush()
                    buffer.clear()

            except asyncio.TimeoutError:
                if buffer:
                    write(b"".join(buffer))
                    flush()
                    buffer.clear()

    if buffer:
        write(b"".join(buffer))
        flush()


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
        def __init__(self, queue, formatter):
            super().__init__()
            self.queue = queue
            self.formatter = formatter

        def emit(self, record):
            try:
                msg = self.formatter.format(record)
                self.queue.put_nowait(msg)
            except Exception:
                self.handleError(record)

    handler = QueueHandler(_LOG_QUEUE, formatter)

    root = logging.getLogger()
    root.setLevel(log_level)
    root.handlers.clear()
    root.addHandler(handler)

    return logging.getLogger(settings.app_name)


log = _setup_logging()


class LoggerMiddleware:
    """Middleware to log request and response details."""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)

        start_time = time.perf_counter()

        log.info(
            "start_process", extra={"method": scope["method"], "path": scope["path"]}
        )

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

        time_process = time.perf_counter() - start_time

        log.info(
            "finish_process",
            extra={
                "method": scope["method"],
                "path": scope["path"],
                "status_code": status_code,
                "time_process": time_process,
            },
        )
