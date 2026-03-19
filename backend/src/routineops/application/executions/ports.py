from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from uuid import UUID

from routineops.domain.entities.execution import Execution, ExecutionStep
from routineops.domain.value_objects.execution_status import ExecutionStatus


class ExecutionRepositoryPort(ABC):
    @abstractmethod
    def list(
        self,
        task_id: UUID | None = None,
        status: ExecutionStatus | None = None,
        scheduled_from: datetime | None = None,
        scheduled_to: datetime | None = None,
    ) -> list[Execution]: ...

    @abstractmethod
    def get(self, execution_id: UUID) -> Execution | None: ...

    @abstractmethod
    def get_with_steps(self, execution_id: UUID) -> Execution | None: ...

    @abstractmethod
    def create(self, execution: Execution) -> Execution: ...

    @abstractmethod
    def update(self, execution: Execution) -> Execution: ...

    @abstractmethod
    def create_step(self, step: ExecutionStep) -> ExecutionStep: ...

    @abstractmethod
    def update_step(self, step: ExecutionStep) -> ExecutionStep: ...
