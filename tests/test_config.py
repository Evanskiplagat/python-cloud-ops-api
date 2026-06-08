import pytest

from app.core.config import Settings


def test_production_requires_non_default_secret_key() -> None:
    with pytest.raises(ValueError, match="CLOUDOPS_SECRET_KEY"):
        Settings(environment="production", secret_key="change-me")


def test_production_rejects_wildcard_cors() -> None:
    with pytest.raises(ValueError, match="CLOUDOPS_CORS_ORIGINS"):
        Settings(
            environment="production",
            secret_key="a-strong-production-secret",
            cors_origins=["*"],
        )


def test_development_allows_local_defaults() -> None:
    settings = Settings(environment="development", cors_origins=["*"])

    assert settings.secret_key == "dev-insecure-secret-key"
    assert settings.cors_origins == ["*"]
