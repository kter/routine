"""Deprecated compatibility alias for task repository port imports."""

from routineops.application.tasks.ports import TaskRepositoryPort as _TaskRepositoryPort

TaskRepositoryPort = _TaskRepositoryPort

__all__ = ["TaskRepositoryPort"]
