import type { PropsWithChildren, ReactNode } from "react";
import { cn } from "@hitech/ui-kit";

export interface SplitPane50Props extends PropsWithChildren {
  readonly left: ReactNode;
  readonly right: ReactNode;
  readonly className?: string;
  readonly leftClassName?: string;
  readonly rightClassName?: string;
  readonly divider?: ReactNode;
}

export function SplitPane50({
  left,
  right,
  className,
  leftClassName,
  rightClassName,
  divider
}: SplitPane50Props) {
  return (
    <div
      className={cn(
        "grid grid-cols-1 gap-4 md:grid-cols-[minmax(0,1fr)_auto_minmax(0,1fr)]",
        className
      )}
    >
      <section className={cn("min-w-0", leftClassName)}>{left}</section>
      <div className="hidden md:flex md:items-stretch">{divider}</div>
      <section className={cn("min-w-0", rightClassName)}>{right}</section>
    </div>
  );
}
