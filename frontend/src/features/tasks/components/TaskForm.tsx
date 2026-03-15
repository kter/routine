import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { CronPicker } from "./CronPicker";
import { StepEditor } from "./StepEditor";
import type { TaskInput, TaskStepInput } from "../types";

const schema = z.object({
  title: z.string().min(1, "タイトルは必須です"),
  description: z.string().optional(),
  cronExpression: z.string().min(1, "スケジュールは必須です"),
  timezone: z.string().default("Asia/Tokyo"),
  estimatedMinutes: z.number().int().positive().default(30),
  tags: z.string().optional(),
});

type FormValues = z.infer<typeof schema>;

interface TaskFormProps {
  defaultValues?: Partial<FormValues>;
  defaultSteps?: TaskStepInput[];
  onSubmit: (data: TaskInput) => Promise<void>;
  submitLabel?: string;
}

export function TaskForm({
  defaultValues,
  defaultSteps = [],
  onSubmit,
  submitLabel = "作成",
}: TaskFormProps) {
  const [steps, setSteps] = useState<TaskStepInput[]>(defaultSteps);
  const [cronExpression, setCronExpression] = useState(
    defaultValues?.cronExpression ?? "0 10 * * *",
  );

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: { ...defaultValues, cronExpression },
  });

  const handleFormSubmit = async (data: FormValues) => {
    await onSubmit({
      ...data,
      cronExpression,
      tags: data.tags
        ? data.tags
            .split(",")
            .map((t) => t.trim())
            .filter(Boolean)
        : [],
      steps,
    });
  };

  return (
    <form onSubmit={handleSubmit(handleFormSubmit)} className="space-y-6">
      <div className="space-y-1">
        <label className="block text-sm font-medium">タイトル *</label>
        <input
          {...register("title")}
          className="w-full rounded-md border bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
        />
        {errors.title && (
          <p className="text-xs text-destructive">{errors.title.message}</p>
        )}
      </div>

      <div className="space-y-1">
        <label className="block text-sm font-medium">説明</label>
        <textarea
          {...register("description")}
          rows={3}
          className="w-full rounded-md border bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
        />
      </div>

      <div className="space-y-1">
        <label className="block text-sm font-medium">スケジュール *</label>
        <CronPicker value={cronExpression} onChange={setCronExpression} />
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-1">
          <label className="block text-sm font-medium">タイムゾーン</label>
          <input
            {...register("timezone")}
            className="w-full rounded-md border bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
          />
        </div>
        <div className="space-y-1">
          <label className="block text-sm font-medium">想定時間（分）</label>
          <input
            type="number"
            {...register("estimatedMinutes", { valueAsNumber: true })}
            className="w-full rounded-md border bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
          />
        </div>
      </div>

      <div className="space-y-1">
        <label className="block text-sm font-medium">
          タグ（カンマ区切り）
        </label>
        <input
          {...register("tags")}
          placeholder="例: 月次, 請求, AWS"
          className="w-full rounded-md border bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
        />
      </div>

      <div className="space-y-2">
        <label className="block text-sm font-medium">ステップ</label>
        <StepEditor steps={steps} onChange={setSteps} />
      </div>

      <div className="flex justify-end">
        <button
          type="submit"
          disabled={isSubmitting}
          className="rounded-md bg-primary px-6 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90 disabled:opacity-50"
        >
          {isSubmitting ? "保存中..." : submitLabel}
        </button>
      </div>
    </form>
  );
}
