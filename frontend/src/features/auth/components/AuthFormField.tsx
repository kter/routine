import type { ComponentProps } from "react";

interface AuthFormFieldProps extends Omit<
  ComponentProps<"input">,
  "className"
> {
  label: string;
  error?: string;
}

export function AuthFormField({
  label,
  error,
  id,
  ...inputProps
}: AuthFormFieldProps) {
  const inputId = id ?? inputProps.name;

  return (
    <div>
      <label htmlFor={inputId} className="block text-sm font-medium">
        {label}
      </label>
      <input
        id={inputId}
        {...inputProps}
        className="mt-1 w-full rounded-md border bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
      />
      {error ? <p className="mt-1 text-xs text-destructive">{error}</p> : null}
    </div>
  );
}
