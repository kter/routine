interface AuthSubmitButtonProps {
  idleLabel: string;
  submittingLabel: string;
  isSubmitting: boolean;
}

export function AuthSubmitButton({
  idleLabel,
  submittingLabel,
  isSubmitting,
}: AuthSubmitButtonProps) {
  return (
    <button
      type="submit"
      disabled={isSubmitting}
      className="w-full rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90 disabled:opacity-50"
    >
      {isSubmitting ? submittingLabel : idleLabel}
    </button>
  );
}
