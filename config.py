from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    prometheus_multiproc_dir: str
    
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')