"""Central registry of v1 schema_version strings."""

from src.schemas.v1.auth import AUTH_SCHEMA_V1
from src.schemas.v1.autodiscover import AUTODISCOVER_SCHEMA_V1
from src.schemas.v1.inventory import INVENTORY_SCHEMA_V1
from src.schemas.v1.meta import META_SCHEMA_V1
from src.schemas.v1.ops import OPS_SCHEMA_V1
from src.schemas.v1.topology import TOPOLOGY_SCHEMA_V1

CORRELATION_SCHEMA_V1 = "rsm-correlation-v1"

SCHEMA_VERSIONS_V1: dict[str, str] = {
    "auth": AUTH_SCHEMA_V1,
    "autodiscover": AUTODISCOVER_SCHEMA_V1,
    "correlation": CORRELATION_SCHEMA_V1,
    "inventory": INVENTORY_SCHEMA_V1,
    "meta": META_SCHEMA_V1,
    "ops": OPS_SCHEMA_V1,
    "topology": TOPOLOGY_SCHEMA_V1,
}
