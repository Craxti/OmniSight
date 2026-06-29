RSM_OFFICIAL_TYPE_NAMES = [
    "Business Service",
    "IT Service",
    "Application",
    "Technical Component",
    "Server",
    "Virtual Machine",
    "Container",
    "Database",
    "Queue",
    "Network Element",
    "External Service",
]

RELATION_TYPES = [
    "depends_on",
    "affects",
    "part_of",
    "hosted_on",
    "uses",
    "linked_to",
    "reserves",
]

RELATION_TYPE_ALIASES = {
    "depends on": "depends_on",
    "affects": "affects",
    "part of": "part_of",
    "hosted on": "hosted_on",
    "uses": "uses",
    "linked to": "linked_to",
    "reserves": "reserves",
}

CI_STATUSES = ["active", "temporarily_disabled", "decommissioned", "archived"]

RELATION_STATUSES = ["active", "inactive", "archived"]

CRITICALITY_LEVELS = ["critical", "high", "medium", "low"]

ENVIRONMENTS = ["production", "pre-production", "test", "development"]

ROLES = ["viewer", "editor", "admin"]

WRITE_ROLES = {"editor", "admin"}
ADMIN_ROLES = {"admin"}

EXTERNAL_ID_FIELDS = [
    "hostname",
    "ip",
    "serviceCode",
    "applicationCode",
    "externalId",
    "cmdbId",
]

FIELD_ALIASES = {
    "host": "hostname",
    "host_name": "hostname",
    "fqdn": "hostname",
    "ip_address": "ip",
    "ipv4": "ip",
    "external_id": "externalId",
    "service_code": "serviceCode",
    "application_code": "applicationCode",
}

EXTERNAL_ID_FIELDS_SET = frozenset(EXTERNAL_ID_FIELDS)

SEARCH_INDEX_FIELDS = tuple(f for f in EXTERNAL_ID_FIELDS if f != "cmdbId")

FIELD_TO_SEARCH_COLUMN = {
    "hostname": "search_hostname",
    "ip": "search_ip",
    "serviceCode": "search_service_code",
    "applicationCode": "search_application_code",
    "externalId": "search_external_id",
}

CACHE_PREFIX_RESOURCE = "resource:"
CACHE_PREFIX_GRAPH = "graph:"
CACHE_PREFIX_RESOLVE = "resolve:"
# Invalidate correlation caches when inventory or topology changes.
CACHE_PREFIXES_CORRELATION = (CACHE_PREFIX_GRAPH, CACHE_PREFIX_RESOLVE)

CI_LIST_SORT_FIELDS = ("id", "name", "status", "environment", "owner", "created_at", "updated_at")

EXPORT_MAX_ROWS = 100_000
