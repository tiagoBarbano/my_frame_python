import logging
import sys
import json_log_formatter
import ujson
from config import Settings


settings = Settings()


def configure_logging():
    logger = logging.getLogger(settings.app_name)
    logger.setLevel(settings.logger_level.upper())

    if (
        settings.logger_level.upper() == "INFO"
        or settings.logger_level.upper() == "WARNING"
    ):
        formatter = json_log_formatter.JSONFormatter()
    elif (
        settings.logger_level.upper() == "DEBUG"
        or settings.logger_level.upper() == "ERROR"
        or settings.logger_level.upper() == "CRITICAL"
    ):
        formatter = json_log_formatter.VerboseJSONFormatter()
    else:
        raise ValueError(f"Nível de log inválido: {settings.logger_level}")

    formatter.json_lib = ujson

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)

    logger.addHandler(stream_handler)
    logger.propagate = False

    return logger


logger = configure_logging()
