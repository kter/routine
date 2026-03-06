import { useState } from "react";
import { tasksApi } from "@/lib/api/tasks";
import type { CreateTaskRequest, UpdateTaskRequest } from "../types";

export function useTaskMutations() {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const createTask = async (data: CreateTaskRequest) => {
    setIsLoading(true);
    setError(null);
    try {
      return await tasksApi.create(data);
    } catch (err) {
      const e = err instanceof Error ? err : new Error("Failed to create task");
      setError(e);
      throw e;
    } finally {
      setIsLoading(false);
    }
  };

  const updateTask = async (id: string, data: UpdateTaskRequest) => {
    setIsLoading(true);
    setError(null);
    try {
      return await tasksApi.update(id, data);
    } catch (err) {
      const e = err instanceof Error ? err : new Error("Failed to update task");
      setError(e);
      throw e;
    } finally {
      setIsLoading(false);
    }
  };

  const deleteTask = async (id: string) => {
    setIsLoading(true);
    setError(null);
    try {
      await tasksApi.delete(id);
    } catch (err) {
      const e = err instanceof Error ? err : new Error("Failed to delete task");
      setError(e);
      throw e;
    } finally {
      setIsLoading(false);
    }
  };

  return { createTask, updateTask, deleteTask, isLoading, error };
}
