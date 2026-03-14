import type {
  DashboardDataDto,
  DashboardTaskDto,
} from "@/lib/api/dto/dashboard";
import type { DashboardData, DashboardTask } from "./types";

function mapDashboardTaskDto(dto: DashboardTaskDto): DashboardTask {
  return {
    taskId: dto.taskId,
    title: dto.title,
    scheduledFor: dto.scheduledFor,
    estimatedMinutes: dto.estimatedMinutes,
    executionId: dto.executionId,
    status: dto.status,
  };
}

export function mapDashboardDataDto(dto: DashboardDataDto): DashboardData {
  return {
    today: dto.today.map(mapDashboardTaskDto),
    overdue: dto.overdue.map(mapDashboardTaskDto),
    upcoming: dto.upcoming.map(mapDashboardTaskDto),
  };
}
