import type { CSSProperties, ReactNode } from "react";

interface PageStateMessageProps {
  title: string;
  description?: ReactNode;
  actionLabel?: string;
  onAction?: () => void;
  className?: string;
  style?: CSSProperties;
  titleClassName?: string;
  titleStyle?: CSSProperties;
  descriptionClassName?: string;
  descriptionStyle?: CSSProperties;
  actionClassName?: string;
  actionStyle?: CSSProperties;
}

export function PageStateMessage({
  title,
  description,
  actionLabel,
  onAction,
  className = "flex h-64 flex-col items-center justify-center gap-3",
  style,
  titleClassName = "font-mono-data text-sm",
  titleStyle,
  descriptionClassName = "text-sm",
  descriptionStyle,
  actionClassName = "font-mono-data text-xs hover:underline",
  actionStyle,
}: PageStateMessageProps) {
  return (
    <div className={className} style={style}>
      <p className={titleClassName} style={titleStyle}>
        {title}
      </p>
      {description ? (
        <p className={descriptionClassName} style={descriptionStyle}>
          {description}
        </p>
      ) : null}
      {actionLabel && onAction ? (
        <button
          onClick={onAction}
          className={actionClassName}
          style={actionStyle}
        >
          {actionLabel}
        </button>
      ) : null}
    </div>
  );
}
