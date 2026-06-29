import pytest
from pydantic import ValidationError
from src.core.config import Settings
from src.core.production import validate_production_settings


def test_production_rejects_insecure_defaults():
    settings = Settings(
        app_env="production",
        database_url="postgresql+psycopg2://u:p@localhost/db",
        secret_key="change-me-in-production",
        api_key="omnisight-api-key-dev",
        webhook_secret="omnisight-webhook-secret-dev",
        cors_origins="https://app.example.com",
    )
    with pytest.raises(RuntimeError, match="SECRET_KEY"):
        validate_production_settings(settings)


def test_settings_reject_sqlite():
    with pytest.raises(ValidationError, match="SQLite"):
        Settings(database_url="sqlite:///./test.db")


def test_development_skips_validation():
    validate_production_settings(
        Settings(
            app_env="development",
            database_url="postgresql+psycopg2://u:p@localhost/db",
            secret_key="change-me-in-production",
        )
    )


def test_development_fills_empty_secrets():
    settings = Settings(
        app_env="development",
        database_url="postgresql+psycopg2://u:p@localhost/db",
        secret_key="",
        api_key="",
        webhook_secret="",
    )
    assert settings.secret_key
    assert settings.api_key
    assert settings.webhook_secret


def test_production_rejects_dev_autofill_secrets():
    dev = Settings(
        app_env="development",
        database_url="postgresql+psycopg2://u:p@localhost/db",
        secret_key="",
        api_key="",
        webhook_secret="",
    )
    with pytest.raises(RuntimeError, match="SECRET_KEY"):
        validate_production_settings(
            Settings(
                app_env="production",
                database_url="postgresql+psycopg2://u:p@localhost/db",
                secret_key=dev.secret_key,
                api_key=dev.api_key,
                webhook_secret=dev.webhook_secret,
                cors_origins="https://app.example.com",
            )
        )
