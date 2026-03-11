from fastapi import APIRouter

from routineops.interface.api.v1.dashboard import router as dashboard_router
from routineops.interface.api.v1.executions import router as executions_router
from routineops.interface.api.v1.tasks import router as tasks_router

router = APIRouter()
router.include_router(tasks_router, prefix="/tasks", tags=["tasks"])
router.include_router(executions_router, prefix="/executions", tags=["executions"])
router.include_router(dashboard_router, prefix="/dashboard", tags=["dashboard"])
