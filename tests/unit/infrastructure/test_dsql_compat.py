import pytest

from routineops.infrastructure.db.dsql_compat import decode_json_array, decode_json_object


def test_decode_json_array_parses_string_values() -> None:
    value = decode_json_array('["ops", "nightly"]')

    assert value == ["ops", "nightly"]


def test_decode_json_array_returns_copy_for_native_lists() -> None:
    source = ["ops"]

    value = decode_json_array(source)
    value.append("nightly")

    assert source == ["ops"]


def test_decode_json_array_returns_empty_list_for_none() -> None:
    assert decode_json_array(None) == []


def test_decode_json_array_rejects_non_array_values() -> None:
    with pytest.raises(ValueError, match="Expected JSON array"):
        decode_json_array('{"unexpected": true}')


def test_decode_json_object_parses_string_values() -> None:
    value = decode_json_object('{"status": "active"}')

    assert value == {"status": "active"}


def test_decode_json_object_returns_copy_for_native_dicts() -> None:
    source = {"status": "active"}

    value = decode_json_object(source)
    value["status"] = "paused"

    assert source == {"status": "active"}


def test_decode_json_object_returns_empty_dict_for_none() -> None:
    assert decode_json_object(None) == {}


def test_decode_json_object_rejects_non_object_values() -> None:
    with pytest.raises(ValueError, match="Expected JSON object"):
        decode_json_object('["unexpected"]')
