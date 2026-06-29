"""Autodiscover relation spec extraction (pure logic)."""

from __future__ import annotations

from src.core.constants import RELATION_TYPES
from src.services.autodiscover.connectors.base import DiscoveredEntity

RELATION_EVIDENCE_CONFIDENCE = {
    "env": 0.96,
    "tcp": 0.94,
    "compose": 0.93,
    "compose_file": 0.92,
    "k8s_service": 0.91,
    "infra": 0.9,
    "docker_network": 0.78,
    "name": 0.72,
}


def extract_relation_specs(entity: DiscoveredEntity) -> list[dict]:
    specs: list[dict] = []
    raw = entity.raw or {}
    relations = raw.get("relations")
    if isinstance(relations, list):
        for item in relations:
            if not isinstance(item, dict):
                continue
            rtype = item.get("type") or item.get("relation_type")
            target = item.get("target_hostname") or item.get("target") or item.get("target_name")
            target_ip = item.get("target_ip") or item.get("ip")
            if rtype and target:
                specs.append(
                    {
                        "relation_type": str(rtype),
                        "target_hostname": str(target).strip(),
                        "target_ip": str(target_ip).strip() if target_ip else None,
                        "evidence": item.get("evidence") or item.get("source"),
                        "confidence": item.get("confidence"),
                    }
                )
    for key in RELATION_TYPES:
        val = raw.get(key)
        if val is None:
            val = entity.fields.get(key)
        if isinstance(val, str) and val.strip():
            specs.append(
                {
                    "relation_type": key,
                    "target_hostname": val.strip(),
                    "target_ip": None,
                    "evidence": "inventory_field",
                    "confidence": None,
                }
            )
    return specs


def relation_confidence(
    *,
    target,
    target_ip: str | None,
    evidence: str | None,
    explicit: float | None,
    in_discovered_batch: bool,
    threshold_auto: float,
) -> tuple[float, str]:
    if explicit is not None:
        confidence = float(explicit)
    elif evidence and evidence in RELATION_EVIDENCE_CONFIDENCE:
        confidence = RELATION_EVIDENCE_CONFIDENCE[evidence]
    elif target:
        confidence = 0.95
    elif in_discovered_batch:
        confidence = 0.88
    else:
        confidence = 0.82
    if target and target_ip and getattr(target, "search_ip", None) == target_ip:
        confidence = max(confidence, 0.97)
    status = "auto" if confidence >= threshold_auto else "needs_confirmation"
    return confidence, status
