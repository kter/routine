"""Deprecated compatibility alias for task application service imports."""

from routineops.application.tasks.service import TaskService

TaskUsecases = TaskService

__all__ = ["TaskUsecases"]
