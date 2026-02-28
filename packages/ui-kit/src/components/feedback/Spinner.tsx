import type { HTMLAttributes } from "react";
import { cn } from "../../lib/cn.js";

export interface SpinnerProps extends HTMLAttributes<HTMLSpanElement> {
  readonly label?: string;
}

export function Spinner({ className, label = "Loading", ...props }: SpinnerProps) {
  return (
    <span
      role="status"
      aria-label={label}
      className={cn("inline-flex items-center gap-2", className)}
      {...props}
    >
      <span className="ui-spinner" aria-hidden />
      <span className="sr-only">{label}</span>
    </span>
  );
}
