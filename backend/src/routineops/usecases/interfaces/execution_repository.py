"""Deprecated compatibility alias for execution repository port imports."""

from routineops.application.executions.ports import (
    ExecutionRepositoryPort as _ExecutionRepositoryPort,
)

ExecutionRepositoryPort = _ExecutionRepositoryPort

__all__ = ["ExecutionRepositoryPort"]
