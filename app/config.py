from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    db_path: str
    azure_openai_endpoint: str
    azure_openai_deployment_name: str
    azure_openai_api_version: str
    azure_openai_key: str
    model_config = SettingsConfigDict(env_file=".env")


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]
