export const queryKeys = {
  dashboard: ["dashboard"] as const,
  tasks: {
    all: ["tasks"] as const,
    detail: (id: string) => ["tasks", id] as const,
  },
  executions: {
    all: ["executions"] as const,
    detail: (id: string) => ["executions", id] as const,
  },
};
