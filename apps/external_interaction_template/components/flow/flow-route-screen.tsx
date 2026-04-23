import type { ReactNode } from "react";

import { cn } from "@/lib/utils";

export function FlowRouteScreen({
  summaryStrip,
  workbench,
  className
}: {
  summaryStrip: ReactNode;
  workbench: ReactNode;
  className?: string;
}) {
  return <section className={cn("flow-route-screen page-stack", className)}>{summaryStrip}{workbench}</section>;
}
