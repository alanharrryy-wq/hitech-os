import { cva, type VariantProps } from "class-variance-authority";
import { forwardRef, type ButtonHTMLAttributes } from "react";
import { cn } from "../../lib/cn.js";
import { FOCUS_RING_CLASS } from "../../lib/focus-ring.js";

const iconButtonVariants = cva(
  [
    "inline-flex items-center justify-center rounded-[var(--ui-core-radius-sm)] border",
    "transition-colors duration-150 disabled:cursor-not-allowed disabled:opacity-50",
    FOCUS_RING_CLASS
  ].join(" "),
  {
    variants: {
      variant: {
        subtle:
          "border-[hsl(var(--ui-border-1))] bg-[hsl(var(--ui-surface-1))] hover:bg-[hsl(var(--ui-surface-2))]",
        ghost: "border-transparent bg-transparent hover:bg-[hsl(var(--ui-surface-2))]"
      },
      size: {
        sm: "h-8 w-8",
        md: "h-9 w-9",
        lg: "h-10 w-10"
      }
    },
    defaultVariants: {
      variant: "subtle",
      size: "md"
    }
  }
);

export interface IconButtonProps
  extends ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof iconButtonVariants> {
  readonly label: string;
}

export const IconButton = forwardRef<HTMLButtonElement, IconButtonProps>(function IconButton(
  { className, variant, size, type = "button", label, ...props },
  ref
) {
  return (
    <button
      ref={ref}
      type={type}
      className={cn(iconButtonVariants({ variant, size }), className)}
      aria-label={label}
      title={label}
      {...props}
    />
  );
});
