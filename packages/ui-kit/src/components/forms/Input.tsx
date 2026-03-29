import { forwardRef, type InputHTMLAttributes } from "react";
import { cn } from "../../lib/cn.js";
import { FOCUS_RING_CLASS } from "../../lib/focus-ring.js";

export type InputProps = InputHTMLAttributes<HTMLInputElement>;

export const Input = forwardRef<HTMLInputElement, InputProps>(function Input(
  { className, type = "text", suppressHydrationWarning = true, ...props },
  ref
) {
  return (
    <input
      ref={ref}
      type={type}
      suppressHydrationWarning={suppressHydrationWarning}
      className={cn(
        "h-9 w-full rounded-[var(--ui-core-radius-sm)] border border-[hsl(var(--ui-border-1))] bg-[hsl(var(--ui-surface-1))] px-3 text-sm text-[hsl(var(--ui-text-1))] placeholder:text-[hsl(var(--ui-text-3))]",
        "transition-colors duration-150 hover:border-[hsl(var(--ui-border-2))]",
        FOCUS_RING_CLASS,
        className
      )}
      {...props}
    />
  );
});
