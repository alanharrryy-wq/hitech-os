import * as React from "react";

import { cn } from "@/lib/utils";

export type TextareaProps = React.TextareaHTMLAttributes<HTMLTextAreaElement>;

export const Textarea = React.forwardRef<HTMLTextAreaElement, TextareaProps>(function Textarea(
  { className, ...props },
  ref
) {
  return (
    <textarea
      ref={ref}
      className={cn(
        "min-h-28 w-full rounded-xl border border-white/12 bg-surface/60 px-3 py-2 text-sm text-text placeholder:text-muted outline-none transition focus:border-accent/40 focus:bg-surface/80 focus:ring-2 focus:ring-accent/35",
        className
      )}
      {...props}
    />
  );
});
