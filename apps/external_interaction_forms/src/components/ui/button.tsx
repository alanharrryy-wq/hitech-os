import type { ButtonHTMLAttributes } from "react";
import { cn } from "@/lib/utils/cn";

type ButtonVariant = "primary" | "secondary" | "ghost";

export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  readonly variant?: ButtonVariant;
}

const variantClasses: Record<ButtonVariant, string> = {
  primary:
    "bg-accent text-white shadow-soft hover:bg-accent/90 focus-visible:ring-accent/35 border-transparent",
  secondary:
    "bg-accentSoft text-ink hover:bg-accentSoft/80 focus-visible:ring-accent/20 border-transparent",
  ghost: "bg-transparent text-muted hover:bg-soft/70 focus-visible:ring-accent/20 border-line/80"
};

export function Button({ className, variant = "primary", type = "button", ...props }: ButtonProps) {
  return (
    <button
      type={type}
      className={cn(
        "inline-flex h-12 items-center justify-center rounded-xl border px-5 text-sm font-semibold tracking-[0.01em] transition focus-visible:outline-none focus-visible:ring-4 disabled:cursor-not-allowed disabled:opacity-60",
        variantClasses[variant],
        className
      )}
      {...props}
    />
  );
}
