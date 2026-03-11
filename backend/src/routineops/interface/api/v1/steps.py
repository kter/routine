from typing import Annotated

from fastapi import APIRouter, Depends

from routineops.interface.api.deps import get_task_usecases
from routineops.usecases.task_usecases import TaskUsecases

router = APIRouter()
TaskUsecasesDep = Annotated[TaskUsecases, Depends(get_task_usecases)]
