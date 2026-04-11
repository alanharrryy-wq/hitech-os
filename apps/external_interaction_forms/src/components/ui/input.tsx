import type { InputHTMLAttributes } from "react";
import { cn } from "@/lib/utils/cn";

export function Input({ className, ...props }: InputHTMLAttributes<HTMLInputElement>) {
  return (
    <input
      className={cn(
        "h-12 w-full rounded-xl border border-line bg-white px-4 text-sm text-ink shadow-sm transition placeholder:text-muted/80 focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-accent/20",
        className
      )}
      {...props}
    />
  );
}
