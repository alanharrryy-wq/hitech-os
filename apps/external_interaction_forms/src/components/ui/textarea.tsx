import type { TextareaHTMLAttributes } from "react";
import { cn } from "@/lib/utils/cn";

export function Textarea({ className, ...props }: TextareaHTMLAttributes<HTMLTextAreaElement>) {
  return (
    <textarea
      className={cn(
        "min-h-32 w-full rounded-xl border border-line bg-white px-4 py-3 text-sm text-ink shadow-sm transition placeholder:text-muted/80 focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-accent/20",
        className
      )}
      {...props}
    />
  );
}
