from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class AutodiscoverScanRequest(BaseModel):
    profile_id: int | None = None
    connector_ids: list[int] | None = None
    server_ci_ids: list[int] | None = Field(default=None, description="Server CI group to scan")
    source_types: list[str] | None = Field(
        default=None,
        description="Connector types filter: host, api, file, db, stream",
    )
    scope_mode: Literal["graph", "filters", "all"] | None = None
    scope_config: dict[str, Any] = Field(default_factory=dict)
    scope_depth: int | None = Field(default=None, ge=0, le=5)
    root_ci_id: int | None = None
    mapping_rules: dict[str, Any] = Field(default_factory=dict)
    discover_relations: bool = True
    create_missing_ci: bool = True
    max_retries: int | None = Field(default=3, ge=1, le=10)
    auto_apply: bool = Field(default=True, description="Auto-apply all mappings except conflicts after scan")


class AutodiscoverFieldMapping(BaseModel):
    mapping_id: str
    mapping_kind: Literal["field", "relation", "ci_create"] = "field"
    ci_id: int | None = None
    ci_name: str
    target_ci_id: int | None = None
    target_ci_name: str | None = None
    relation_type: str | None = None
    field: str
    current_value: str | None = None
    discovered_value: str
    source_server: str
    source_connector: str = ""
    confidence: float = Field(ge=0.0, le=1.0)
    status: Literal["auto", "needs_confirmation", "conflict", "unchanged", "applied"]
    selected: bool = False


class AutodiscoverSourceReport(BaseModel):
    connector_id: int | None = None
    connector_name: str | None = None
    connector_type: str | None = None
    server_ci_id: int | None = None
    server_name: str | None = None
    hostname: str | None = None
    ok: bool
    records_found: int = 0
    error: str | None = None
    duration_ms: int = 0
    attempts: int = 0


class AutodiscoverApplyResponse(BaseModel):
    applied: int
    skipped: int
    errors: list[str] = Field(default_factory=list)
    updated_ci_ids: list[int] = Field(default_factory=list)
    created_cis: int = 0
    applied_relations: int = 0


class AutodiscoverScanResponse(BaseModel):
    run_id: int
    status: str
    sources_processed: int
    sources_ok: int
    fields_found: int
    auto_count: int
    needs_confirmation_count: int
    conflict_count: int
    relation_count: int = 0
    ci_create_count: int = 0
    sources: list[AutodiscoverSourceReport]
    mappings: list[AutodiscoverFieldMapping]
    discovered_schema: dict[str, Any] = Field(default_factory=dict)
    schema_diff: dict[str, Any] | None = None
    apply_result: AutodiscoverApplyResponse | None = None


class AutodiscoverApplyRequest(BaseModel):
    mapping_ids: list[str] | None = None
    apply_auto_only: bool = False


class SyncConnectorCredentials(BaseModel):
    """Write-only credentials. Prefer *_env fields in production."""

    auth_type: Literal["none", "basic", "bearer", "api_key", "ssh_key"] = "none"
    username: str | None = None
    password: str | None = None
    username_env: str | None = None
    password_env: str | None = None
    private_key: str | None = None
    private_key_path: str | None = None
    private_key_path_env: str | None = None
    token: str | None = None
    token_env: str | None = None
    api_key: str | None = None
    api_key_env: str | None = None
    api_key_header: str | None = "X-API-Key"
    database_url: str | None = None
    database_url_env: str | None = None


class SyncConnectorCreate(BaseModel):
    name: str = Field(min_length=1, max_length=128)
    connector_type: Literal["api", "file", "db", "stream", "host"]
    server_ci_id: int | None = None
    config: dict[str, Any] = Field(default_factory=dict)
    credentials: SyncConnectorCredentials | None = None
    timeout_seconds: int = Field(default=30, ge=1, le=300)
    max_retries: int = Field(default=3, ge=1, le=10)
    enabled: bool = True
    auto_sync: bool = Field(default=False, description="Periodically pull and apply discovered data")


class SyncConnectorUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=128)
    server_ci_id: int | None = None
    config: dict[str, Any] | None = None
    credentials: SyncConnectorCredentials | None = None
    timeout_seconds: int | None = Field(default=None, ge=1, le=300)
    max_retries: int | None = Field(default=None, ge=1, le=10)
    enabled: bool | None = None
    auto_sync: bool | None = None


class SyncConnectorTestResponse(BaseModel):
    ok: bool
    records_found: int = 0
    error: str | None = None
    duration_ms: int = 0


class SyncConnectorSyncResponse(BaseModel):
    run_id: int
    status: str
    sources_ok: int = 0
    fields_found: int = 0
    apply_result: AutodiscoverApplyResponse | None = None
    error: str | None = None


class SyncConnectorResponse(BaseModel):
    id: int
    name: str
    connector_type: str
    server_ci_id: int | None = None
    config: dict[str, Any] = Field(default_factory=dict)
    has_credentials: bool = False
    timeout_seconds: int
    max_retries: int
    read_only: bool
    enabled: bool
    auto_sync: bool = False
    schema_version: str


class SyncProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None = None
    connector_ids: list[int] = Field(default_factory=list)
    source_types: list[str] = Field(default_factory=list)
    scope_mode: str
    scope_config: dict[str, Any] = Field(default_factory=dict)
    mapping_rules: dict[str, Any] = Field(default_factory=dict)
    auto_apply_threshold: float
    schema_version: str
    last_run_id: int | None = None


class AutodiscoverRunSummary(BaseModel):
    id: int
    profile_id: int | None = None
    status: str
    user_email: str | None = None
    report: dict[str, Any] = Field(default_factory=dict)
    created_at: str | None = None
    completed_at: str | None = None
