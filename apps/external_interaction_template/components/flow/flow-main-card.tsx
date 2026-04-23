import type { ReactNode } from "react";

import { cn } from "@/lib/utils";

export function FlowMainCard({
  children,
  className
}: {
  children: ReactNode;
  className?: string;
}) {
  return <section className={cn("flow-main-card", className)}>{children}</section>;
}
