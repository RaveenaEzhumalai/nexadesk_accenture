"""NexaDesk — Configuration (reads from .env file)"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    app_name: str = "NexaDesk"
    app_version: str = "2.0.0"
    environment: str = "development"
    debug: bool = True
    host: str = "0.0.0.0"
    port: int = 8000
    secret_key: str = "nexadesk-super-secret-key-minimum-32-characters-long"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440
    database_url: str = "sqlite:///./nexadesk.db"
    allowed_origins: str = "http://localhost:3000,http://localhost:5500,http://127.0.0.1:5500,http://127.0.0.1:3000,null"
    rate_limit_per_minute: int = 100
    admin_email: str = "admin@nexadesk.com"
    admin_password: str = "Admin@123"
    admin_name: str = "System Administrator"
    auto_resolve_confidence_threshold: float = 0.75
    max_agent_processing_time_seconds: int = 30

    @property
    def cors_origins(self) -> List[str]:
        return [o.strip() for o in self.allowed_origins.split(",")]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"


settings = Settings()
