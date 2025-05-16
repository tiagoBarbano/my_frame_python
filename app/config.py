from functools import lru_cache
from pydantic import Field

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    prometheus_multiproc_dir: str | None = Field(default="metrics", validate_default=False)
    app_name: str = Field(default="My Granian FrameWork", validate_default=False)
    logger_level: str = Field(default="INFO", validate_default=False)
    endpoint_otel: str = Field(default="http://localhost:4317", validate_default=False)
    flag_local: bool = Field(default=False, validate_default=False)
    enable_tracing: bool = Field(default=False, validate_default=False)
    enable_metrics: bool = Field(default=False, validate_default=False)
    enable_logger: bool = Field(default=False, validate_default=False)
    enable_swagger: bool = Field(default=True, validate_default=False)
    enable_trace_ratio_based: bool = Field(default=True, validate_default=False)
    ratio_value: str = Field(default=0.05, validate_default=False)
    redis_url: str = Field(default="redis://:redis1234@localhost:6379", validate_default=False)
    mongo_url: str = Field(default="mongodb://localhost:27017", validate_default=False)
    mongo_db: str = Field(default="cotador", validate_default=False)
    redis_ttl: int = Field(default=10, validate_default=False)
    worker: int = Field(default=1, validate_default=False)
    granian_runtime_mode: str = Field(default="st", validate_default=False)

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache()
def get_settings():
    return Settings()
