import { cva, type VariantProps } from "class-variance-authority";
import type { HTMLAttributes } from "react";
import { cn } from "../lib/cn.js";

const textVariants = cva("", {
  variants: {
    size: {
      xs: "text-xs",
      sm: "text-sm",
      md: "text-base",
      lg: "text-lg"
    },
    tone: {
      default: "text-[hsl(var(--ui-text-2))]",
      muted: "text-[hsl(var(--ui-text-3))]",
      strong: "text-[hsl(var(--ui-text-1))]",
      success: "text-[hsl(var(--ui-success))]",
      danger: "text-[hsl(var(--ui-danger))]"
    }
  },
  defaultVariants: {
    size: "md",
    tone: "default"
  }
});

export interface TextProps extends HTMLAttributes<HTMLElement>, VariantProps<typeof textVariants> {
  readonly as?: "p" | "span" | "strong" | "small";
}

export function Text({ as = "p", className, size, tone, ...props }: TextProps) {
  const Comp = as;
  return <Comp className={cn(textVariants({ size, tone }), className)} {...props} />;
}
