from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from routineops.domain.entities.execution import Execution, ExecutionStep
from routineops.domain.value_objects.execution_status import ExecutionStatus


class ExecutionRepositoryPort(ABC):
    @abstractmethod
    def list(
        self,
        tenant_id: UUID,
        task_id: UUID | None = None,
        status: ExecutionStatus | None = None,
    ) -> list[Execution]:
        ...

    @abstractmethod
    def get(self, tenant_id: UUID, execution_id: UUID) -> Execution | None:
        ...

    @abstractmethod
    def get_with_steps(self, tenant_id: UUID, execution_id: UUID) -> Execution | None:
        ...

    @abstractmethod
    def create(self, execution: Execution) -> Execution:
        ...

    @abstractmethod
    def update(self, execution: Execution) -> Execution:
        ...

    @abstractmethod
    def create_step(self, step: ExecutionStep) -> ExecutionStep:
        ...

    @abstractmethod
    def update_step(self, step: ExecutionStep) -> ExecutionStep:
        ...
