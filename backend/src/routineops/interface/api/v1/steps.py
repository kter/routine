from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from routineops.domain.exceptions import NotFoundError, ValidationError
from routineops.interface.api.deps import TenantDep, get_task_usecases
from routineops.interface.schemas.task import StepResponse, CreateStepRequest
from routineops.interface.schemas.step import UpdateStepRequest
from routineops.usecases.task_usecases import TaskUsecases

router = APIRouter()
TaskUsecasesDep = Annotated[TaskUsecases, Depends(get_task_usecases)]
