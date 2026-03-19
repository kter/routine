from typing import Annotated

from fastapi import APIRouter, Depends

from routineops.application.tasks import TaskService
from routineops.interface.api.deps import get_task_usecases

router = APIRouter()
TaskServiceDep = Annotated[TaskService, Depends(get_task_usecases)]
