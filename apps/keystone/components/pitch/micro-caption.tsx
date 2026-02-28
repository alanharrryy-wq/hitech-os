import type { PropsWithChildren } from "react";
import { cn } from "@hitech/ui-kit";

export interface MicroCaptionProps extends PropsWithChildren {
  readonly className?: string;
}

export function MicroCaption({ className, children }: MicroCaptionProps) {
  return (
    <p
      className={cn(
        "m-0 text-xs font-medium leading-snug tracking-[0.02em] text-[hsl(var(--ui-text-3))]",
        className
      )}
    >
      {children}
    </p>
  );
}
