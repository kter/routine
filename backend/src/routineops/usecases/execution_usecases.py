"""Deprecated compatibility alias for execution application service imports."""

from routineops.application.executions.service import ExecutionService

ExecutionUsecases = ExecutionService

__all__ = ["ExecutionUsecases"]
