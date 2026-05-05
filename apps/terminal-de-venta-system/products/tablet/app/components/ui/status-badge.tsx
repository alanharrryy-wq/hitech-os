import type { ReactNode } from "react";
import { cn } from "@/lib/utils";

export function StatusBadge({ tone, children }: { tone: "ok" | "warn" | "danger"; children: ReactNode }) {
  return <span className={cn("badge", tone)}>{children}</span>;
}
