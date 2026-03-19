from uuid import UUID, uuid4

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from routineops.infrastructure.db import models as _models  # noqa: F401
from routineops.infrastructure.db.base import Base
from routineops.infrastructure.db.dsql_compat import (
    JsonArrayText,
    JsonObjectText,
    decode_json_array,
    decode_json_object,
)
from routineops.infrastructure.db.models.execution_step_model import ExecutionStepModel
from routineops.infrastructure.db.models.task_model import TaskModel


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


@pytest.fixture
def sqlite_session() -> Session:
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    session = Session(engine)
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(engine)
        engine.dispose()


def test_json_array_text_round_trips_python_lists(sqlite_session: Session) -> None:
    assert isinstance(TaskModel.__table__.c.tags.type, JsonArrayText)
    assert isinstance(TaskModel.__table__.c.metadata.type, JsonObjectText)

    task = TaskModel(
        id=uuid4(),
        tenant_id=UUID("00000000-0000-0000-0000-000000000001"),
        title="task",
        description="",
        cron_expression="0 10 * * *",
        timezone="UTC",
        estimated_minutes=30,
        is_active=True,
        tags=["ops", "nightly"],
        metadata_={"source": "test"},
        created_by="tester",
    )
    sqlite_session.add(task)
    sqlite_session.commit()

    stored_task = sqlite_session.execute(select(TaskModel)).scalar_one()

    assert stored_task.tags == ["ops", "nightly"]
    assert stored_task.metadata_ == {"source": "test"}


def test_json_object_text_round_trips_step_snapshot(sqlite_session: Session) -> None:
    assert isinstance(ExecutionStepModel.__table__.c.step_snapshot.type, JsonObjectText)

    step = ExecutionStepModel(
        id=uuid4(),
        tenant_id=UUID("00000000-0000-0000-0000-000000000001"),
        execution_id=UUID("00000000-0000-0000-0000-000000000010"),
        step_id=UUID("00000000-0000-0000-0000-000000000020"),
        position=1,
        step_snapshot={"title": "check", "is_required": True, "evidence_type": "none"},
        status="pending",
        evidence_text=None,
        evidence_image_key=None,
        completed_at=None,
        completed_by=None,
        notes="",
    )
    sqlite_session.add(step)
    sqlite_session.commit()

    stored_step = sqlite_session.execute(select(ExecutionStepModel)).scalar_one()

    assert stored_step.step_snapshot == {
        "title": "check",
        "is_required": True,
        "evidence_type": "none",
    }
