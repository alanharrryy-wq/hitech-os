import { cva, type VariantProps } from "class-variance-authority";
import { forwardRef, type ButtonHTMLAttributes } from "react";
import { cn } from "../../../lib/cn.js";
import { FOCUS_RING_CLASS } from "../../../lib/focus-ring.js";

const neonButtonVariants = cva(
  [
    "ui-neon-button inline-flex items-center justify-center gap-2 whitespace-nowrap",
    "disabled:cursor-not-allowed disabled:opacity-50",
    FOCUS_RING_CLASS
  ].join(" "),
  {
    variants: {
      variant: {
        primary: "",
        secondary: "",
        ghost: ""
      },
      size: {
        sm: "px-3 py-2 text-xs",
        md: "px-4 py-2.5 text-sm",
        lg: "px-5 py-3 text-sm"
      },
      glow: {
        soft: "ui-premium-glow-020",
        medium: "ui-premium-glow-040",
        strong: "ui-premium-glow-strong-058"
      }
    },
    compoundVariants: [
      {
        variant: "primary",
        className: "ui-premium-gradient-subtle-011"
      },
      {
        variant: "secondary",
        className: "ui-premium-gradient-subtle-021"
      },
      {
        variant: "ghost",
        className: "bg-[rgba(244,248,251,0.22)]"
      }
    ],
    defaultVariants: {
      variant: "primary",
      size: "md",
      glow: "soft"
    }
  }
);

export interface NeonButtonProps
  extends ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof neonButtonVariants> {
  readonly loading?: boolean;
}

export const NeonButton = forwardRef<HTMLButtonElement, NeonButtonProps>(function NeonButton(
  { className, variant, size, glow, type = "button", loading = false, disabled, children, ...props },
  ref
) {
  const isDisabled = disabled || loading;
  return (
    <button
      ref={ref}
      type={type}
      className={cn(neonButtonVariants({ variant, size, glow }), className)}
      data-variant={variant}
      disabled={isDisabled}
      aria-busy={loading ? true : undefined}
      {...props}
    >
      {loading ? (
        <span
          className="inline-block h-3 w-3 animate-spin rounded-full border border-current border-r-transparent"
          aria-hidden="true"
        />
      ) : null}
      <span>{children}</span>
    </button>
  );
});
