import * as React from "react";

import { cn } from "@/lib/utils";

export type InputProps = React.InputHTMLAttributes<HTMLInputElement>;

export const Input = React.forwardRef<HTMLInputElement, InputProps>(function Input({ className, ...props }, ref) {
  return (
    <input
      ref={ref}
      className={cn(
        "h-10 w-full rounded-xl border border-white/12 bg-surface/60 px-3 text-sm text-text placeholder:text-muted outline-none transition focus:border-accent/40 focus:bg-surface/80 focus:ring-2 focus:ring-accent/35",
        className
      )}
      {...props}
    />
  );
});
