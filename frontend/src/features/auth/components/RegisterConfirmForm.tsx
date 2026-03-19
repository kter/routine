import type { UseFormReturn } from "react-hook-form";
import type { ConfirmValues } from "../schemas/register";
import { AuthFormError } from "./AuthFormError";
import { AuthFormField } from "./AuthFormField";
import { AuthSubmitButton } from "./AuthSubmitButton";

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
      <AuthFormField
        label="確認コード"
        type="text"
        inputMode="numeric"
        error={form.formState.errors.code?.message}
        {...form.register("code")}
      />
      <AuthFormError message={error} />
      <AuthSubmitButton
        idleLabel="確認"
        submittingLabel="確認中..."
        isSubmitting={form.formState.isSubmitting}
      />
    </form>
  );
}
