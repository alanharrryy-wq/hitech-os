import { cva, type VariantProps } from "class-variance-authority";
import { forwardRef, type ButtonHTMLAttributes } from "react";
import { cn } from "../../lib/cn.js";
import { FOCUS_RING_CLASS } from "../../lib/focus-ring.js";

const buttonVariants = cva(
  [
    "inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-[var(--ui-core-radius-sm)]",
    "border border-transparent px-3 py-2 text-sm font-medium transition-colors duration-150",
    "disabled:cursor-not-allowed disabled:opacity-50",
    FOCUS_RING_CLASS
  ].join(" "),
  {
    variants: {
      variant: {
        solid:
          "bg-[hsl(var(--ui-accent))] text-white hover:bg-[hsl(var(--ui-accent)/0.9)] active:bg-[hsl(var(--ui-accent)/0.85)]",
        subtle:
          "bg-[hsl(var(--ui-surface-2))] text-[hsl(var(--ui-text-1))] border-[hsl(var(--ui-border-1))] hover:bg-[hsl(var(--ui-surface-3))]",
        outline:
          "bg-transparent text-[hsl(var(--ui-text-2))] border-[hsl(var(--ui-border-2))] hover:bg-[hsl(var(--ui-surface-2))]",
        ghost: "bg-transparent text-[hsl(var(--ui-text-2))] hover:bg-[hsl(var(--ui-surface-2))]",
        primary:
          "bg-[hsl(var(--ui-accent))] text-white hover:bg-[hsl(var(--ui-accent)/0.9)] active:bg-[hsl(var(--ui-accent)/0.85)]",
        secondary:
          "bg-[hsl(var(--ui-surface-2))] text-[hsl(var(--ui-text-1))] border-[hsl(var(--ui-border-1))] hover:bg-[hsl(var(--ui-surface-3))]"
      },
      size: {
        sm: "h-8 px-2.5 text-xs",
        md: "h-9 px-3 text-sm",
        lg: "h-10 px-4 text-sm"
      }
    },
    defaultVariants: {
      variant: "solid",
      size: "md"
    }
  }
);

export interface ButtonProps
  extends ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(function Button(
  { className, variant, size, type = "button", ...props },
  ref
) {
  return (
    <button
      ref={ref}
      type={type}
      className={cn(buttonVariants({ variant, size }), className)}
      {...props}
    />
  );
});
