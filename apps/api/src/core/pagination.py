"""Shared pagination metadata helpers."""

from __future__ import annotations

import math


def pagination_meta(total_items: int, page: int, page_size: int) -> dict[str, int]:
    total_pages = max(1, math.ceil(total_items / page_size)) if page_size else 1
    return {
        "page": page,
        "page_size": page_size,
        "total_items": total_items,
        "total_pages": total_pages,
    }
