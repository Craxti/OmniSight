"""Development-only secret placeholders.

These values are injected when ``APP_ENV != production`` and the corresponding
setting is empty. They must never pass ``validate_production_settings``.
"""

DEV_SECRET_KEY = "dev-only-omnisight-secret-do-not-use-in-prod"
DEV_API_KEY = "dev-only-omnisight-api-key"
DEV_WEBHOOK_SECRET = "dev-only-omnisight-webhook-secret"

DEV_SECRET_VALUES = frozenset(
    {
        DEV_SECRET_KEY,
        DEV_API_KEY,
        DEV_WEBHOOK_SECRET,
        # Legacy dev defaults kept for migration from older .env files
        "change-me-in-production-omnisight-rsm-secret",
        "change-me-in-development-only",
        "omnisight-api-key-dev",
        "omnisight-webhook-secret-dev",
    }
)
