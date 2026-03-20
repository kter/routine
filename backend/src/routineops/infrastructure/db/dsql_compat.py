from __future__ import annotations

import json
from collections.abc import Sequence

from sqlalchemy import Text
from sqlalchemy.engine import Dialect
from sqlalchemy.types import TypeDecorator

JsonArray = list[object]
JsonObject = dict[str, object]


class JsonArrayText(TypeDecorator[list[object]]):
    """Persist JSON arrays in TEXT columns for Aurora DSQL compatibility."""

    impl = Text
    cache_ok = True

    def process_bind_param(
        self,
        value: Sequence[object] | str | None,
        dialect: Dialect,
    ) -> str | None:
        del dialect
        if value is None:
            return None
        return json.dumps(decode_json_array(value))

    def process_result_value(
        self,
        value: str | list[object] | None,
        dialect: Dialect,
    ) -> list[object] | None:
        del dialect
        if value is None:
            return None
        return decode_json_array(value)


class JsonObjectText(TypeDecorator[dict[str, object]]):
    """Persist JSON objects in TEXT columns for Aurora DSQL compatibility."""

    impl = Text
    cache_ok = True

    def process_bind_param(
        self,
        value: JsonObject | str | None,
        dialect: Dialect,
    ) -> str | None:
        del dialect
        if value is None:
            return None
        return json.dumps(decode_json_object(value))

    def process_result_value(
        self,
        value: JsonObject | str | None,
        dialect: Dialect,
    ) -> JsonObject | None:
        del dialect
        if value is None:
            return None
        return decode_json_object(value)


def decode_json_array(value: Sequence[object] | str | None) -> JsonArray:
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
