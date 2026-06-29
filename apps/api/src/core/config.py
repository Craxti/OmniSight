from typing import Self

from pydantic import AliasChoices, Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from src.core.dev_secrets import DEV_API_KEY, DEV_SECRET_KEY, DEV_WEBHOOK_SECRET


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore", populate_by_name=True)

    app_name: str = "OmniSight RSM"
    app_env: str = "development"
    database_url: str = "postgresql+psycopg2://postgres:7002@localhost:5432/omnisight"
    secret_key: str = ""
    access_token_expire_minutes: int = 60 * 24
    api_key: str = ""
    webhook_secret: str = ""
    webhook_url: str = ""
    integration_user_email: str = "integration@omnisight.local"
    database_read_url: str = ""
    cache_enabled: bool = True
    cache_ttl_seconds: int = 30
    cors_origins: str = "http://localhost:5173,http://localhost:3000"
    log_level: str = "INFO"
    log_json: bool = False
    docs_enabled: bool = True
    trusted_hosts: str = ""
    rate_limit_max_requests: int = 200
    rate_limit_window_seconds: int = 60
    rate_limit_enabled: bool = True
    uvicorn_workers: int = 1
    admin_initial_password: str = ""
    auto_sync_scheduler_enabled: bool = True
    auto_sync_interval_seconds: int = 300
    background_tasks_enabled: bool = False
    webhook_sync_delivery: bool = True
    outbox_poll_interval_seconds: int = 15
    outbox_max_attempts: int = 5
    outbox_batch_size: int = 20
    redis_url: str = ""
    database_async_enabled: bool = True
    ensure_schema_on_start: bool = Field(
        default=True,
        validation_alias=AliasChoices("ENSURE_SCHEMA_ON_START", "RUN_MIGRATIONS_ON_START"),
    )
    database_pool_size: int = 5
    database_max_overflow: int = 10

    @field_validator("app_env")
    @classmethod
    def normalize_env(cls, value: str) -> str:
        return value.strip().lower()

    @field_validator("database_url")
    @classmethod
    def require_postgresql(cls, value: str) -> str:
        if value.strip().lower().startswith("sqlite"):
            raise ValueError("SQLite is not supported; use PostgreSQL in DATABASE_URL")
        return value

    @model_validator(mode="after")
    def apply_env_defaults(self) -> Self:
        """§9 NFR + FR 43: в production всегда JSON-логи и OpenAPI."""
        if self.is_production:
            self.log_json = True
            self.docs_enabled = True
            return self

        if not self.secret_key.strip():
            self.secret_key = DEV_SECRET_KEY
        if not self.api_key.strip():
            self.api_key = DEV_API_KEY
        if not self.webhook_secret.strip():
            self.webhook_secret = DEV_WEBHOOK_SECRET
        return self

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"

    @property
    def trusted_hosts_list(self) -> list[str]:
        return [h.strip() for h in self.trusted_hosts.split(",") if h.strip()]

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


settings = Settings()
