import * as React from "react";

import { cn } from "@/lib/utils";

type ButtonVariant = "primary" | "secondary" | "ghost" | "danger";

const variantClass: Record<ButtonVariant, string> = {
  primary:
    "bg-accent/20 text-accent border border-accent/35 hover:bg-accent/28 active:bg-accent/34 shadow-glow",
  secondary:
    "bg-surface/70 text-text border border-white/10 hover:bg-surface/80 active:bg-surface/90",
  ghost:
    "bg-transparent text-muted hover:text-text hover:bg-white/5 border border-transparent",
  danger:
    "bg-danger/20 text-danger border border-danger/35 hover:bg-danger/30 active:bg-danger/40"
};

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(function Button(
  { className, variant = "secondary", type = "button", ...props },
  ref
) {
  return (
    <button
      ref={ref}
      type={type}
      className={cn(
        "inline-flex h-9 items-center justify-center rounded-xl px-3 text-sm font-medium tracking-wide transition duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent/60 disabled:pointer-events-none disabled:opacity-45",
        variantClass[variant],
        className
      )}
      {...props}
    />
  );
});
