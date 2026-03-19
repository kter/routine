import type { UseFormReturn } from "react-hook-form";
import type { ConfirmValues } from "../schemas/register";

interface RegisterConfirmFormProps {
  email: string;
  error: string | null;
  form: UseFormReturn<ConfirmValues>;
  onSubmit: (data: ConfirmValues) => Promise<void>;
}

export function RegisterConfirmForm({
  email,
  error,
  form,
  onSubmit,
}: RegisterConfirmFormProps) {
  return (
    <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
      <p className="text-sm text-muted-foreground">
        <span className="font-medium">{email}</span>{" "}
        に確認コードを送信しました。
      </p>
      <div>
        <label className="block text-sm font-medium">確認コード</label>
        <input
          type="text"
          inputMode="numeric"
          {...form.register("code")}
          className="mt-1 w-full rounded-md border bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
        />
        {form.formState.errors.code && (
          <p className="mt-1 text-xs text-destructive">
            {form.formState.errors.code.message}
          </p>
        )}
      </div>
      {error && <p className="text-sm text-destructive">{error}</p>}
      <button
        type="submit"
        disabled={form.formState.isSubmitting}
        className="w-full rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90 disabled:opacity-50"
      >
        {form.formState.isSubmitting ? "確認中..." : "確認"}
      </button>
    </form>
  );
}
