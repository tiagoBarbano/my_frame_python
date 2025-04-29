from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    prometheus_multiproc_dir: str | None = None
    app_name: str
    logger_level: str = "WARNING"
    endpoint_otel: str = "http://localhost:4317"
    flag_local: bool = False
    enable_tracing: bool = False
    enable_metrics: bool = True
    enable_logger: bool = False
    enable_swagger: bool = True

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
