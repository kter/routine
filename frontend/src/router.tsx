import { AppShell } from "@/components/layout/AppShell";
import { ProtectedRoute } from "@/features/auth";
import { createAppRouter } from "@/lib/monitoring/sentry";
import LoginPage from "@/pages/LoginPage";
import RegisterPage from "@/pages/RegisterPage";
import DashboardPage from "@/pages/DashboardPage";
import TasksPage from "@/pages/TasksPage";
import TaskDetailPage from "@/pages/TaskDetailPage";
import TaskNewPage from "@/pages/TaskNewPage";
import TaskEditPage from "@/pages/TaskEditPage";
import ExecutionPage from "@/pages/ExecutionPage";
import ExecutionListPage from "@/pages/ExecutionListPage";
import ExecutionLogPage from "@/pages/ExecutionLogPage";

export const router = createAppRouter([
  {
    path: "/login",
    element: <LoginPage />,
  },
  {
    path: "/register",
    element: <RegisterPage />,
  },
  {
    path: "/",
    element: (
      <ProtectedRoute>
        <AppShell />
      </ProtectedRoute>
    ),
    children: [
      {
        index: true,
        element: <DashboardPage />,
      },
      {
        path: "tasks",
        element: <TasksPage />,
      },
      {
        path: "tasks/new",
        element: <TaskNewPage />,
      },
      {
        path: "tasks/:id",
        element: <TaskDetailPage />,
      },
      {
        path: "tasks/:id/edit",
        element: <TaskEditPage />,
      },
      {
        path: "executions",
        element: <ExecutionListPage />,
      },
      {
        path: "executions/:id",
        element: <ExecutionPage />,
      },
      {
        path: "executions/:id/log",
        element: <ExecutionLogPage />,
      },
    ],
  },
]);
