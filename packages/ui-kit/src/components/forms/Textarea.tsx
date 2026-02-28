import { forwardRef, type TextareaHTMLAttributes } from "react";
import { cn } from "../../lib/cn.js";
import { FOCUS_RING_CLASS } from "../../lib/focus-ring.js";

export type TextareaProps = TextareaHTMLAttributes<HTMLTextAreaElement>;

export const Textarea = forwardRef<HTMLTextAreaElement, TextareaProps>(function Textarea(
  { className, rows = 4, ...props },
  ref
) {
  return (
    <textarea
      ref={ref}
      rows={rows}
      className={cn(
        "w-full rounded-[var(--ui-core-radius-sm)] border border-[hsl(var(--ui-border-1))] bg-[hsl(var(--ui-surface-1))] px-3 py-2 text-sm text-[hsl(var(--ui-text-1))] placeholder:text-[hsl(var(--ui-text-3))]",
        "transition-colors duration-150 hover:border-[hsl(var(--ui-border-2))]",
        FOCUS_RING_CLASS,
        className
      )}
      {...props}
    />
  );
});
