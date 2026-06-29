"""HTTP webhook delivery (blocking I/O — run via ``asyncio.to_thread``)."""

from __future__ import annotations

import json
import logging
import urllib.error
import urllib.request
from typing import Any

logger = logging.getLogger("omnisight.webhook")


def deliver_webhook(url: str, payload: dict[str, Any], secret: str | None = None) -> bool:
    data = json.dumps(payload).encode()
    req = urllib.request.Request(url, data=data, method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("User-Agent", "OmniSight-RSM/1.0")
    if secret:
        req.add_header("X-Webhook-Secret", secret)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return 200 <= resp.status < 300
    except urllib.error.HTTPError as exc:
        logger.warning("webhook HTTP %s → %s", url, exc.code)
        return False
    except Exception as exc:
        logger.warning("webhook failed → %s: %s", url, exc)
        return False
