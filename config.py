from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    prometheus_multiproc_dir: str | None = None
    app_name: str
    logger_level: str
    
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')