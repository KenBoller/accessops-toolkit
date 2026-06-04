"""
AccessOps Toolkit - ID Generator
--------------------------------
Shared helper for generating predictable mock IDs across JSON-backed records.
"""

from typing import Any


def get_next_id(
    records: list[dict[str, Any]],
    default_start: int,
    id_field: str = "id",
) -> int:
    """Return the next numeric ID from a list of record dictionaries."""
    if not records:
        return default_start

    existing_ids = []

    for record in records:
        try:
            existing_ids.append(int(record.get(id_field)))
        except (TypeError, ValueError):
            continue

    if not existing_ids:
        return default_start

    return max(existing_ids) + 1