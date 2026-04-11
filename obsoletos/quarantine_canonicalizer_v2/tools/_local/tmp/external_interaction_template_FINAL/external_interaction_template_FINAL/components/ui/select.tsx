import * as React from "react";

import { cn } from "@/lib/utils";

export type SelectProps = React.SelectHTMLAttributes<HTMLSelectElement>;

export const Select = React.forwardRef<HTMLSelectElement, SelectProps>(function Select({ className, ...props }, ref) {
  return (
    <select
      ref={ref}
      className={cn(
        "h-10 w-full rounded-xl border border-white/12 bg-surface/60 px-3 text-sm text-text outline-none transition focus:border-accent/40 focus:bg-surface/80 focus:ring-2 focus:ring-accent/35",
        className
      )}
      {...props}
    />
  );
});
