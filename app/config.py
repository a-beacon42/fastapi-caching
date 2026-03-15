from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    db_path: str
    llm_endpoint: str
    azure_openai_key: str
    model_config = SettingsConfigDict(env_file=".env")
