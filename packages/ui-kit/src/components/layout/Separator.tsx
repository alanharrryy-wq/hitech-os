import type { HTMLAttributes } from "react";
import { cn } from "../../lib/cn.js";

export interface SeparatorProps extends HTMLAttributes<HTMLHRElement> {
  readonly orientation?: "horizontal" | "vertical";
  readonly className?: string;
}

export function Separator({ className, orientation = "horizontal", ...props }: SeparatorProps) {
  if (orientation === "vertical") {
    return (
      <span
        className={cn("inline-block h-full w-px bg-[hsl(var(--ui-border-1))]", className)}
        {...props}
      />
    );
  }

  return <hr className={cn("ui-separator", className)} {...props} />;
}
