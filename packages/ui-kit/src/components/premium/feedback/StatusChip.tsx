import { cva, type VariantProps } from "class-variance-authority";
import type { HTMLAttributes, ReactNode } from "react";
import { cn } from "../../../lib/cn.js";

export type StatusChipState = "pass" | "block" | "hold" | "critical";

const statusChipVariants = cva("ui-status-chip", {
  variants: {
    status: {
      pass: "",
      block: "",
      hold: "",
      critical: ""
    },
    emphasis: {
      subtle: "opacity-90",
      solid: "opacity-100"
    }
  },
  defaultVariants: {
    status: "pass",
    emphasis: "subtle"
  }
});

export interface StatusChipProps
  extends Omit<HTMLAttributes<HTMLSpanElement>, "children">,
    VariantProps<typeof statusChipVariants> {
  readonly label: ReactNode;
  readonly dot?: boolean;
}

export function StatusChip({ className, status, emphasis, label, dot = true, ...props }: StatusChipProps) {
  return (
    <span className={cn(statusChipVariants({ status, emphasis }), className)} data-status={status} {...props}>
      {dot ? <span className="h-1.5 w-1.5 rounded-full bg-current" aria-hidden="true" /> : null}
      <span>{label}</span>
    </span>
  );
}

export type ChipGroupProps = HTMLAttributes<HTMLDivElement>;

export function ChipGroup({ className, children, ...props }: ChipGroupProps) {
  return (
    <div className={cn("flex flex-wrap items-center gap-2", className)} {...props}>
      {children}
    </div>
  );
}
