def normalize_relation_filter(relation_filter: str | None) -> str:
    value = (relation_filter or "").strip()
    return value or "*"
