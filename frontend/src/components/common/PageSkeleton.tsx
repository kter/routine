import type { CSSProperties } from "react";

export interface SkeletonBlock {
  className: string;
  style?: CSSProperties;
}

interface PageSkeletonProps {
  blocks: SkeletonBlock[];
  className?: string;
}

export function PageSkeleton({
  blocks,
  className = "space-y-4 animate-fade-up",
}: PageSkeletonProps) {
  return (
    <div className={className}>
      {blocks.map((block, index) => (
        <div
          key={`${block.className}-${index}`}
          className={block.className}
          style={block.style}
        />
      ))}
    </div>
  );
}
