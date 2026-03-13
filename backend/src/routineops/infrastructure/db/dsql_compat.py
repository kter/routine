from __future__ import annotations

import json

JsonArray = list[object]
JsonObject = dict[str, object]


def decode_json_array(value: JsonArray | str | None) -> JsonArray:
    """Normalize Aurora DSQL TEXT-backed JSON arrays into Python lists."""
    if value is None:
        return []

    parsed = json.loads(value) if isinstance(value, str) else value
    if not isinstance(parsed, list):
        raise ValueError("Expected JSON array")

    return list(parsed)


def decode_json_object(value: JsonObject | str | None) -> JsonObject:
    """Normalize Aurora DSQL TEXT-backed JSON objects into Python dicts."""
    if value is None:
        return {}

    parsed = json.loads(value) if isinstance(value, str) else value
    if not isinstance(parsed, dict):
        raise ValueError("Expected JSON object")

    return dict(parsed)
