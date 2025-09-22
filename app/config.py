from functools import lru_cache
from pydantic import Field

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    prometheus_multiproc_dir: str | None = Field(
        default="metrics",
        validate_default=False,
        description="Directory for Prometheus multiprocess mode",
    )
    app_name: str = Field(
        default="My Granian FrameWork",
        validate_default=False,
        description="Name of the application",
    )
    logger_level: str = Field(
        default="INFO",
        validate_default=False,
        description="Logging level for the application",
    )
    endpoint_otel: str = Field(
        default="http://localhost:4317",
        validate_default=False,
        description="Endpoint for OpenTelemetry or Grafana Tempo",
    )
    flag_local: bool = Field(
        default=False,
        validate_default=False,
        description="Flag to indicate if the application is running in local mode",
    )
    enable_tracing: bool = Field(
        default=True, validate_default=False, description="Enable or disable tracing"
    )
    enable_metrics: bool = Field(
        default=True,
        validate_default=False,
        description="Enable or disable metrics collection",
    )
    enable_logger: bool = Field(
        default=False,
        validate_default=False,
        description="Enable or disable logging middleware",
    )
    enable_swagger: bool = Field(
        default=True, validate_default=False, description="Enable or disable Swagger UI"
    )
    enable_trace_ratio_based: bool = Field(
        default=True,
        validate_default=False,
        description="Enable or disable ratio-based tracing - limits the number of traces sent to the tracing system",
    )
    ratio_value: str = Field(
        default=0.1,
        validate_default=False,
        description="Ratio value for ratio-based tracing - percentage of requests to trace - if enable_trace_ratio_based is True",
    )
    redis_url: str = Field(
        default="redis://:redis1234@localhost:6379",
        validate_default=False,
        description="URL for Redis instance",
    )
    mongo_url: str = Field(
        default="mongodb://localhost:27017",
        validate_default=False,
        description="URL for MongoDB instance",
    )
    mongo_db: str = Field(
        default="cotador",
        validate_default=False,
        description="Name of the MongoDB database",
    )
    redis_ttl: int = Field(
        default=1,
        validate_default=False,
        description="Time-to-live for Redis keys in seconds",
        example=1,
    )
    worker: int = Field(
        default=1,
        validate1default=False,
        description="Number of worker processes",
        example=1,
    )
    granian_runtime_mode: str = Field(
        default="st",
        validate_default=False,
        description="Granian runtime mode (st for single-threaded, mt for multi-threaded)",
        example="st",
    )
    port_app: int = Field(
        default=8001,
        validate_default=False,
        description="Port for the application to listen on",
        example=8001,
    )
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache()
def get_settings():
    return Settings()
