from datetime import UTC, datetime
from uuid import UUID, uuid4

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from routineops.domain.entities.execution import ExecutionStep
from routineops.domain.value_objects.execution_status import StepStatus
from routineops.infrastructure.db import models as _models  # noqa: F401
from routineops.infrastructure.db.base import Base
from routineops.infrastructure.db.models.execution_step_model import ExecutionStepModel
from routineops.infrastructure.db.models.task_model import TaskModel
from routineops.infrastructure.repositories.execution_repository_impl import ExecutionRepositoryImpl
from routineops.infrastructure.repositories.task_repository_impl import TaskRepositoryImpl

TENANT_ID = UUID("00000000-0000-0000-0000-000000000001")
OTHER_TENANT_ID = UUID("00000000-0000-0000-0000-000000000002")


@pytest.fixture
def db_session() -> Session:
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    session = factory()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(engine)
        engine.dispose()


def test_task_repository_rejects_mismatched_tenant_id(db_session: Session) -> None:
    repo = TaskRepositoryImpl(db_session, TENANT_ID)

    with pytest.raises(ValueError, match="Repository tenant mismatch"):
        repo.list(OTHER_TENANT_ID)


def test_execution_repository_rejects_mismatched_tenant_id(db_session: Session) -> None:
    repo = ExecutionRepositoryImpl(db_session, TENANT_ID)

    with pytest.raises(ValueError, match="Repository tenant mismatch"):
        repo.get(OTHER_TENANT_ID, uuid4())


def test_execution_repository_update_step_is_tenant_scoped(db_session: Session) -> None:
    foreign_step_id = uuid4()
    now = datetime.now(tz=UTC)
    db_session.add(
        ExecutionStepModel(
            id=foreign_step_id,
            tenant_id=OTHER_TENANT_ID,
            execution_id=uuid4(),
            step_id=uuid4(),
            position=1,
            step_snapshot={"title": "foreign", "evidence_type": "none", "is_required": True},
            status="pending",
            evidence_text=None,
            evidence_image_key=None,
            completed_at=None,
            completed_by=None,
            notes="",
            created_at=now,
            updated_at=now,
        )
    )
    db_session.commit()

    repo = ExecutionRepositoryImpl(db_session, TENANT_ID)
    step = ExecutionStep(
        id=foreign_step_id,
        tenant_id=TENANT_ID,
        execution_id=uuid4(),
        step_id=uuid4(),
        position=1,
        step_snapshot={"title": "updated", "evidence_type": "none", "is_required": True},
        status=StepStatus.COMPLETED,
        evidence_text="done",
        evidence_image_key=None,
        completed_at=now,
        completed_by="tenant-a",
        notes="",
        created_at=now,
        updated_at=now,
    )

    with pytest.raises(ValueError, match=f"ExecutionStep {foreign_step_id} not found"):
        repo.update_step(step)


def test_task_repository_delete_is_tenant_scoped(db_session: Session) -> None:
    foreign_task_id = uuid4()
    now = datetime.now(tz=UTC)
    db_session.add(
        TaskModel(
            id=foreign_task_id,
            tenant_id=OTHER_TENANT_ID,
            title="foreign-task",
            description="",
            cron_expression="0 10 * * *",
            timezone="UTC",
            estimated_minutes=30,
            is_active=True,
            tags=[],
            metadata_={},
            created_by="tenant-b",
            created_at=now,
            updated_at=now,
        )
    )
    db_session.commit()

    repo = TaskRepositoryImpl(db_session, TENANT_ID)
    repo.delete(TENANT_ID, foreign_task_id)

    remaining = (
        db_session.query(TaskModel)
        .filter(TaskModel.id == foreign_task_id, TaskModel.tenant_id == OTHER_TENANT_ID)
        .one_or_none()
    )
    assert remaining is not None
