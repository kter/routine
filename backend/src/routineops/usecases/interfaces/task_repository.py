from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from routineops.domain.entities.task import Task, Step


class TaskRepositoryPort(ABC):
    @abstractmethod
    def list(self, tenant_id: UUID, active_only: bool = False) -> list[Task]:
        ...

    @abstractmethod
    def get(self, tenant_id: UUID, task_id: UUID) -> Task | None:
        ...

    @abstractmethod
    def get_with_steps(self, tenant_id: UUID, task_id: UUID) -> Task | None:
        ...

    @abstractmethod
    def create(self, task: Task) -> Task:
        ...

    @abstractmethod
    def update(self, task: Task) -> Task:
        ...

    @abstractmethod
    def delete(self, tenant_id: UUID, task_id: UUID) -> None:
        ...

    @abstractmethod
    def list_steps(self, tenant_id: UUID, task_id: UUID) -> list[Step]:
        ...

    @abstractmethod
    def create_step(self, step: Step) -> Step:
        ...

    @abstractmethod
    def update_step(self, step: Step) -> Step:
        ...

    @abstractmethod
    def delete_step(self, tenant_id: UUID, step_id: UUID) -> None:
        ...
