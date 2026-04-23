import type { ReactNode } from "react";
import { cn } from "@/lib/utils";

export function FlowStep({
  step,
  title,
  description,
  tone = "ok",
  aside,
}: {
  step: string;
  title: string;
  description: string;
  tone?: "ok" | "warn" | "danger";
  aside?: ReactNode;
}) {
  return (
    <div className={cn("flow-step", `tone-${tone}`)}>
      <div className="flow-step-badge">{step}</div>
      <div>
        <strong>{title}</strong>
        <div className="subtle">{description}</div>
      </div>
      {aside ? <div className="flow-step-aside">{aside}</div> : null}
    </div>
  );
}
