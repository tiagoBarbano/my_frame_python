from pydantic import Field

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    prometheus_multiproc_dir: str | None = Field(default=None, validate_default=False)
    app_name: str
    logger_level: str = Field(default="WARNING", validate_default=False)
    endpoint_otel: str = Field(default="http://localhost:4317", validate_default=False)
    flag_local: bool = Field(default=True, validate_default=False)
    enable_tracing: bool = Field(default=True, validate_default=False)
    enable_metrics: bool = Field(default=True, validate_default=False)
    enable_logger: bool = Field(default=False, validate_default=False)
    enable_swagger: bool = Field(default=True, validate_default=False)

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
