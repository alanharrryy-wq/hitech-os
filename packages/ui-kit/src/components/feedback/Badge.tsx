import { cva, type VariantProps } from "class-variance-authority";
import type { HTMLAttributes } from "react";
import { cn } from "../../lib/cn.js";

const badgeVariants = cva("ui-badge", {
  variants: {
    tone: {
      neutral: "",
      accent: "",
      success: "",
      warning: "",
      danger: ""
    }
  },
  defaultVariants: {
    tone: "neutral"
  }
});

export interface BadgeProps
  extends HTMLAttributes<HTMLSpanElement>,
    VariantProps<typeof badgeVariants> {}

export function Badge({ className, tone, ...props }: BadgeProps) {
  return <span className={cn(badgeVariants({ tone }), className)} data-tone={tone} {...props} />;
}
