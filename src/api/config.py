import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    HASHING_ITERATIONS: int
    JWT_SIGNATURE: str
    TOKEN_EXPIRY_HOURS: int

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        extra='ignore'
    )

settings = Settings()
