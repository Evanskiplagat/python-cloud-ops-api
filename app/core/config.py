from functools import lru_cache

from pydantic import Field
from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        env_prefix="CLOUDOPS_",
    )

    app_name: str = "CloudOps Center"
    environment: str = "development"
    debug: bool = False
    api_v1_prefix: str = "/api/v1"

    database_url: str = Field(
        default="postgresql+psycopg://cloudops:cloudops@postgres:5432/cloudops_center"
    )
    redis_url: str = "redis://redis:6379/0"

    secret_key: str = "dev-insecure-secret-key"
    access_token_expire_minutes: int = 60
    refresh_token_expire_minutes: int = 60 * 24 * 7
    algorithm: str = "HS256"

    cors_origins: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_security_defaults(self) -> "Settings":
        is_development = self.environment.lower() == "development"
        insecure_secret_keys = {"", "change-me", "dev-insecure-secret-key"}

        if not is_development and self.secret_key in insecure_secret_keys:
            raise ValueError("CLOUDOPS_SECRET_KEY must be set to a strong value outside development")

        if not is_development and "*" in self.cors_origins:
            raise ValueError("CLOUDOPS_CORS_ORIGINS cannot contain '*' outside development")

        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
