"""Repository protocols for dependency inversion and testing."""

from __future__ import annotations

from typing import Any, Protocol

from src.models import CI, AutodiscoverMapping, AutodiscoverRun, CIType, Relation, SyncConnector, SyncProfile, User


class CiReadRepositoryProtocol(Protocol):
    """Read-only CI persistence surface."""

    def get_active(self, ci_id: int) -> CI | None: ...

    def get_or_404(self, ci_id: int, *, include_deleted: bool = False) -> CI: ...

    def get_by_name(self, name: str, *, include_deleted: bool = False) -> CI | None: ...

    def list_active(self, *, limit: int = 10_000) -> list[CI]: ...

    def list_in_ids(
        self,
        ci_ids: set[int],
        *,
        environment: str | None = None,
        owner: str | None = None,
    ) -> list[CI]: ...

    def list_deleted(self) -> list[CI]: ...

    def count_active(self) -> int: ...

    def count_active_by_type(self, type_id: int) -> int: ...

    def list_recycled_by_type(self, type_id: int) -> list[CI]: ...

    def search(self, **kwargs: object) -> tuple[list[CI], int]: ...

    def find_by_search_field(self, field: str, value: str, *, exclude_ci_id: int | None = None) -> CI | None: ...


class CiRepositoryProtocol(CiReadRepositoryProtocol, Protocol):
    def name_exists(self, name: str, *, exclude_id: int | None = None) -> bool: ...

    def list_active_ids(self) -> set[int]: ...

    def archived_active_ids(self) -> set[int]: ...

    def find_for_alert_conditions(self, conditions: list) -> list[CI]: ...


class CITypeRepositoryProtocol(Protocol):
    def get_by_id(self, type_id: int) -> CIType | None: ...

    def get_by_name(self, name: str) -> CIType | None: ...

    def require_by_id(self, type_id: int) -> CIType: ...

    def require_by_name(self, name: str) -> CIType: ...

    def list_ordered(self) -> list[CIType]: ...


class RelationCrudRepositoryProtocol(Protocol):
    def get_active(self, relation_id: int) -> Relation | None: ...

    def list_active(self) -> list[Relation]: ...

    def list_active_page(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
        relation_type: str | None = None,
        status: str | None = None,
        data_source: str | None = None,
        source_name: str | None = None,
        target_name: str | None = None,
        q: str | None = None,
    ) -> tuple[list[Relation], int]: ...

    def touching_ci_ids(self, ci_ids: set[int]) -> list[Relation]: ...

    def find_active(
        self,
        source_ci_id: int,
        target_ci_id: int,
        relation_type: str,
    ) -> Relation | None: ...

    def for_ci(self, ci_id: int) -> list[Relation]: ...

    def list_active_non_archived(self) -> list[Relation]: ...

    def delete_for_ci(self, ci_id: int) -> None: ...


class RelationTopologyRepositoryProtocol(Protocol):
    def list_depends_on_edges(self) -> list[tuple[int, int]]: ...

    def dependency_adjacency(
        self,
        *,
        ci_ids: set[int] | None = None,
        relation_types: tuple[str, ...],
    ) -> tuple[dict[int, set[int]], dict[int, set[int]]]: ...

    def list_incoming_with_source(
        self,
        target_ci_ids: set[int],
        relation_types: tuple[str, ...],
    ) -> list[Relation]: ...


class RelationRepositoryProtocol(RelationCrudRepositoryProtocol, RelationTopologyRepositoryProtocol, Protocol):
    pass


class AuditRepositoryProtocol(Protocol):
    def search(
        self,
        *,
        entity_type: str | None = None,
        action: str | None = None,
        user_email: str | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[list[Any], int]: ...

    def for_entity(self, entity_type: str, entity_id: int, *, limit: int = 50) -> list[Any]: ...

    def for_ci_with_relations(self, ci_id: int, *, limit: int = 50) -> list[Any]: ...

    def log(
        self,
        *,
        entity_type: str,
        entity_id: int | None,
        action: str,
        user_email: str | None,
        old_value: dict[str, Any] | None = None,
        new_value: dict[str, Any] | None = None,
    ) -> Any: ...


class UserRepositoryProtocol(Protocol):
    def get_by_email(self, email: str) -> User | None: ...

    def count_admins(self) -> int: ...

    def count_all(self) -> int: ...

    def list_ordered(self) -> list[User]: ...


class SyncConnectorRepositoryProtocol(Protocol):
    def get_by_id(self, connector_id: int) -> SyncConnector | None: ...

    def get_by_name(self, name: str) -> SyncConnector | None: ...

    def list_ordered(self, *, enabled_only: bool = True) -> list[SyncConnector]: ...


class SyncProfileRepositoryProtocol(Protocol):
    def get_by_name(self, name: str) -> SyncProfile | None: ...

    def list_all(self) -> list[SyncProfile]: ...


class AutodiscoverRunRepositoryProtocol(Protocol):
    def get_by_id(self, run_id: int) -> AutodiscoverRun | None: ...

    def get_with_mappings(self, run_id: int) -> AutodiscoverRun | None: ...

    def list_recent(self, limit: int = 20) -> list[AutodiscoverRun]: ...


class AutodiscoverMappingRepositoryProtocol(Protocol):
    def list_for_run(self, run_id: int) -> list[AutodiscoverMapping]: ...

    def list_auto_apply_ids(self, run_id: int) -> list[str]: ...

    def list_pending_for_apply(
        self,
        run_id: int,
        *,
        mapping_ids: list[str] | None = None,
        apply_auto_only: bool = False,
    ) -> list[AutodiscoverMapping]: ...


# --- Async repository protocols (native ``await``; used by ``async_read`` / handlers) ---


class AsyncCiReadRepositoryProtocol(Protocol):
    async def get_active(self, ci_id: int) -> CI | None: ...

    async def get_or_404(self, ci_id: int, *, include_deleted: bool = False) -> CI: ...

    async def get_detail_or_404(self, ci_id: int, *, include_deleted: bool = False) -> CI: ...

    async def list_in_ids(
        self,
        ci_ids: set[int],
        *,
        environment: str | None = None,
        owner: str | None = None,
    ) -> list[CI]: ...

    async def search(self, **kwargs: object) -> tuple[list[CI], int]: ...


class AsyncRelationTopologyRepositoryProtocol(Protocol):
    async def dependency_adjacency(
        self,
        *,
        ci_ids: set[int] | None = None,
        relation_types: tuple[str, ...],
    ) -> tuple[dict[int, set[int]], dict[int, set[int]]]: ...

    async def list_incoming_with_source(
        self,
        target_ci_ids: set[int],
        relation_types: tuple[str, ...],
    ) -> list[Relation]: ...

    async def list_depends_on_edges(self) -> list[tuple[int, int]]: ...


class AsyncRelationRepositoryProtocol(AsyncRelationTopologyRepositoryProtocol, Protocol):
    async def list_active_page(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
        relation_type: str | None = None,
        status: str | None = None,
        data_source: str | None = None,
        source_name: str | None = None,
        target_name: str | None = None,
        q: str | None = None,
    ) -> tuple[list[Relation], int]: ...

    async def for_ci(self, ci_id: int) -> list[Relation]: ...

    async def touching_ci_ids(self, ci_ids: set[int]) -> list[Relation]: ...


class AsyncAuditRepositoryProtocol(Protocol):
    async def search(
        self,
        *,
        entity_type: str | None = None,
        action: str | None = None,
        user_email: str | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[list[Any], int]: ...

    async def for_entity(self, entity_type: str, entity_id: int, *, limit: int = 50) -> list[Any]: ...

    async def for_ci_with_relations(self, ci_id: int, *, limit: int = 50) -> list[Any]: ...


class AsyncCITypeRepositoryProtocol(Protocol):
    async def get_by_id(self, type_id: int) -> CIType | None: ...

    async def list_ordered(self) -> list[CIType]: ...


class AsyncUserRepositoryProtocol(Protocol):
    async def get_by_email(self, email: str) -> User | None: ...

    async def list_ordered(self) -> list[User]: ...
