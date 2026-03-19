interface AuthPanelHeaderProps {
  title: string;
  eyebrow: string;
}

export function AuthPanelHeader({ title, eyebrow }: AuthPanelHeaderProps) {
  return (
    <div className="mb-6 text-center">
      <h2
        className="font-brand text-lg tracking-tight"
        style={{ color: "hsl(210 20% 90%)", fontWeight: 700 }}
      >
        {title}
      </h2>
      <p
        className="mt-1 font-mono-data text-[11px] tracking-wide"
        style={{ color: "hsl(215 16% 38%)" }}
      >
        {eyebrow}
      </p>
    </div>
  );
}
