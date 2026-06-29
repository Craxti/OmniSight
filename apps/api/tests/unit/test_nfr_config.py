from src.core.config import Settings


def test_production_always_enables_json_logs_and_openapi():
    """§9 NFR + FR 43: production cannot disable JSON logs or Swagger."""
    settings = Settings(
        app_env="production",
        log_json=False,
        docs_enabled=False,
        cors_origins="https://app.example.com",
    )
    assert settings.log_json is True
    assert settings.docs_enabled is True


def test_development_respects_log_and_docs_flags():
    settings = Settings(app_env="development", log_json=False, docs_enabled=False)
    assert settings.log_json is False
    assert settings.docs_enabled is False
