import type { InputHTMLAttributes } from "react";
import { cn } from "@/lib/utils/cn";

export function Checkbox({ className, ...props }: InputHTMLAttributes<HTMLInputElement>) {
  return (
    <input
      type="checkbox"
      className={cn(
        "h-5 w-5 rounded border-line text-accent focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-accent/20",
        className
      )}
      {...props}
    />
  );
}
