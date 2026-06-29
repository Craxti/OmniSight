"""Production startup checks."""

from src.core.config import Settings
from src.core.dev_secrets import DEV_SECRET_VALUES

_INSECURE_SECRETS = DEV_SECRET_VALUES | frozenset({"change-me-in-production"})


def validate_production_settings(settings: Settings) -> None:
    if not settings.is_production:
        return

    errors: list[str] = []

    if settings.secret_key in _INSECURE_SECRETS or len(settings.secret_key) < 32:
        errors.append("SECRET_KEY must be a unique random string of at least 32 characters")

    if settings.api_key in _INSECURE_SECRETS or len(settings.api_key) < 24:
        errors.append("API_KEY must be a unique random string of at least 24 characters")

    if settings.webhook_secret in _INSECURE_SECRETS or len(settings.webhook_secret) < 24:
        errors.append("WEBHOOK_SECRET must be a unique random string of at least 24 characters")

    if not settings.cors_origins.strip():
        errors.append("CORS_ORIGINS must be set explicitly in production")

    if errors:
        raise RuntimeError("Production configuration is unsafe:\n- " + "\n- ".join(errors))
